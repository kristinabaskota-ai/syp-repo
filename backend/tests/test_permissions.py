import pytest
from app.models import User, Product, Category


def test_anonymous_permissions(client):
    # Allowed
    assert client.get("/products").status_code == 200
    assert client.get("/products/categories").status_code == 200
    assert client.get("/import-check?country=Nepal").status_code == 200
    assert client.get("/doctor/symptoms").status_code == 200

    # Denied (401)
    assert client.get("/cart").status_code == 401
    assert client.post("/orders/checkout", json={"shipping_address": "Test", "destination_country": "Nepal"}).status_code == 401
    assert client.get("/orders/my").status_code == 401
    assert client.post("/products", json={"category_id": 1, "name": "Test", "description": "test", "price": 10, "stock": 1, "light_requirement": "low"}).status_code == 401
    assert client.get("/users").status_code == 401
    assert client.get("/reports").status_code == 401


def test_buyer_permissions(client, buyer_headers):
    # Buyer allowed cart and orders
    assert client.get("/cart", headers=buyer_headers).status_code == 200
    assert client.get("/orders/my", headers=buyer_headers).status_code == 200

    # Buyer denied seller endpoints (403)
    resp = client.post("/products", headers=buyer_headers, json={
        "category_id": 1,
        "name": "Buyer Plant",
        "description": "Should fail",
        "price": 100.0,
        "stock": 5,
        "light_requirement": "low"
    })
    assert resp.status_code == 403

    # Buyer denied admin endpoints (403)
    assert client.get("/users", headers=buyer_headers).status_code == 403
    assert client.get("/reports", headers=buyer_headers).status_code == 403
    assert client.post("/import-rules", headers=buyer_headers, json={
        "country": "Test",
        "plant_name": "*",
        "required_documents": "Doc"
    }).status_code == 403


def test_unapproved_seller_denied(client):
    # Register unapproved seller
    client.post("/auth/register", json={
        "full_name": "Unapproved Seller",
        "email": "unapproved@example.com",
        "password": "Password123",
        "role": "seller"
    })
    login_resp = client.post("/auth/login", json={"email": "unapproved@example.com", "password": "Password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to create product listing -> 403 pending approval
    resp = client.post("/products", headers=headers, json={
        "category_id": 1,
        "name": "Illegal Listing",
        "description": "Unapproved seller listing",
        "price": 500.0,
        "stock": 10,
        "light_requirement": "low"
    })
    assert resp.status_code == 403
    assert "pending approval" in resp.json()["detail"].lower()


def test_seller_cannot_edit_others_listings(client, seller_headers, admin_headers):
    # Get a product
    prods = client.get("/products").json()
    assert len(prods) > 0
    prod_id = prods[0]["id"]

    # Register a second approved seller
    client.post("/auth/register", json={
        "full_name": "Second Seller",
        "email": "seller2@example.com",
        "password": "Password123",
        "role": "seller"
    })
    # Admin approves seller2
    users = client.get("/users", headers=admin_headers).json()
    seller2_id = [u["id"] for u in users if u["email"] == "seller2@example.com"][0]
    client.patch(f"/users/{seller2_id}/approve", headers=admin_headers, json={"is_approved": True})

    # Seller 2 logs in
    s2_login = client.post("/auth/login", json={"email": "seller2@example.com", "password": "Password123"})
    s2_token = s2_login.json()["access_token"]
    s2_headers = {"Authorization": f"Bearer {s2_token}"}

    # Seller 2 attempts to edit Seller 1's listing -> 403
    resp = client.put(f"/products/{prod_id}", headers=s2_headers, json={"name": "Hacked Name"})
    assert resp.status_code == 403
    assert "own listings" in resp.json()["detail"].lower()


def test_seller_denied_admin_reports(client, seller_headers):
    assert client.get("/reports", headers=seller_headers).status_code == 403
    assert client.get("/users", headers=seller_headers).status_code == 403


def test_admin_cannot_deactivate_self(client, admin_headers):
    me = client.get("/users/me", headers=admin_headers).json()
    admin_id = me["id"]
    resp = client.patch(f"/users/{admin_id}/status", headers=admin_headers, json={"is_active": False})
    assert resp.status_code == 400
    assert "cannot deactivate" in resp.json()["detail"].lower()


def test_admin_cannot_change_own_role(client, admin_headers):
    me = client.get("/users/me", headers=admin_headers).json()
    admin_id = me["id"]
    resp = client.patch(f"/users/{admin_id}/role", headers=admin_headers, json={"role": "buyer"})
    assert resp.status_code == 400
    assert "cannot change their own role" in resp.json()["detail"].lower()


def test_deactivated_user_blocked(client, admin_headers):
    # Register buyer
    client.post("/auth/register", json={
        "full_name": "To Deactivate",
        "email": "deactivate@example.com",
        "password": "Password123",
        "role": "buyer"
    })
    users = client.get("/users", headers=admin_headers).json()
    target_id = [u["id"] for u in users if u["email"] == "deactivate@example.com"][0]

    # Deactivate user
    client.patch(f"/users/{target_id}/status", headers=admin_headers, json={"is_active": False})

    # Login attempt
    resp = client.post("/auth/login", json={"email": "deactivate@example.com", "password": "Password123"})
    assert resp.status_code == 403
    assert "deactivated" in resp.json()["detail"].lower()
