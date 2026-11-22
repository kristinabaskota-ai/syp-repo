import pytest
from app.models import Product, Order, OrderItem


def test_catalogue_list_and_detail(client):
    resp = client.get("/products")
    assert resp.status_code == 200
    products = resp.json()
    assert len(products) >= 20

    first_id = products[0]["id"]
    detail = client.get(f"/products/{first_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == first_id


def test_search_products_by_name(client):
    resp = client.get("/products?search=Monstera")
    assert resp.status_code == 200
    prods = resp.json()
    assert any("Monstera" in p["name"] for p in prods)


def test_filter_products_by_category(client):
    cats = client.get("/products/categories").json()
    rare_cat = [c for c in cats if c["name"] == "Rare"][0]

    resp = client.get(f"/products?category_id={rare_cat['id']}")
    assert resp.status_code == 200
    prods = resp.json()
    assert all(p["category_id"] == rare_cat["id"] for p in prods)


def test_filter_products_by_light_and_pet_safe(client):
    resp = client.get("/products?light_requirement=bright&pet_safe=true")
    assert resp.status_code == 200
    prods = resp.json()
    for p in prods:
        assert p["light_requirement"] == "bright"
        assert p["pet_safe"] is True


def test_filter_products_by_tree_purpose(client):
    resp = client.get("/products?tree_purpose=timber")
    assert resp.status_code == 200
    prods = resp.json()
    assert len(prods) > 0
    assert all(p["tree_purpose"] == "timber" for p in prods)


def test_seller_create_and_update_listing(client, seller_headers):
    cats = client.get("/products/categories").json()
    indoor_cat = [c for c in cats if c["name"] == "Indoor"][0]

    # Create listing
    create_resp = client.post("/products", headers=seller_headers, json={
        "category_id": indoor_cat["id"],
        "name": "Custom Seller Fern",
        "description": "Lush green indoor fern specimen",
        "price": 1450.0,
        "stock": 10,
        "light_requirement": "medium",
        "pet_safe": True
    })
    assert create_resp.status_code == 201
    created_id = create_resp.json()["id"]

    # Update listing
    update_resp = client.put(f"/products/{created_id}", headers=seller_headers, json={
        "price": 1350.0,
        "stock": 15
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["price"] == 1350.0
    assert update_resp.json()["stock"] == 15

    # Toggle active
    toggle_resp = client.patch(f"/products/{created_id}/toggle-active", headers=seller_headers)
    assert toggle_resp.status_code == 200
    assert toggle_resp.json()["is_active"] is False


def test_delete_product_without_orders_deletes_record(client, seller_headers):
    cats = client.get("/products/categories").json()
    create_resp = client.post("/products", headers=seller_headers, json={
        "category_id": cats[0]["id"],
        "name": "Ephemeral Plant",
        "description": "Will be deleted immediately",
        "price": 999.0,
        "stock": 5,
        "light_requirement": "low"
    })
    prod_id = create_resp.json()["id"]

    del_resp = client.delete(f"/products/{prod_id}", headers=seller_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["action"] == "deleted"

    # Confirm it's gone
    assert client.get(f"/products/{prod_id}").status_code == 404


def test_delete_product_with_orders_hides_record(client, seller_headers, buyer_headers):
    cats = client.get("/products/categories").json()
    create_resp = client.post("/products", headers=seller_headers, json={
        "category_id": cats[0]["id"],
        "name": "Purchased Plant",
        "description": "Will be bought then deleted",
        "price": 500.0,
        "stock": 10,
        "light_requirement": "low"
    })
    prod_id = create_resp.json()["id"]

    # Buyer purchases it
    client.post("/orders/buy-now", headers=buyer_headers, json={
        "product_id": prod_id,
        "quantity": 1,
        "shipping_address": "Kathmandu, Nepal",
        "destination_country": "Nepal"
    })

    # Seller attempts to delete it -> should be hidden instead
    del_resp = client.delete(f"/products/{prod_id}", headers=seller_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["action"] == "hidden"
    assert del_resp.json()["is_active"] is False

    # Still accessible by direct ID but marked inactive
    detail = client.get(f"/products/{prod_id}").json()
    assert detail["is_active"] is False
