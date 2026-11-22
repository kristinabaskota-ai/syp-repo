import pytest
from app.models import Product


def test_checkout_empty_cart_fails(client, buyer_headers):
    client.delete("/cart", headers=buyer_headers)
    resp = client.post("/orders/checkout", headers=buyer_headers, json={
        "shipping_address": "Kathmandu, Nepal",
        "destination_country": "Nepal"
    })
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"].lower()


def test_checkout_stock_deduction_and_cart_clearing(client, buyer_headers):
    client.delete("/cart", headers=buyer_headers)
    prods = client.get("/products").json()
    p1 = prods[0]
    p2 = prods[1]

    initial_stock_p1 = p1["stock"]
    initial_stock_p2 = p2["stock"]

    # Add to cart
    client.post("/cart", headers=buyer_headers, json={"product_id": p1["id"], "quantity": 1})
    client.post("/cart", headers=buyer_headers, json={"product_id": p2["id"], "quantity": 2})

    # Checkout
    order_resp = client.post("/orders/checkout", headers=buyer_headers, json={
        "shipping_address": "Baluwatar, Kathmandu",
        "destination_country": "Nepal"
    })
    assert order_resp.status_code == 201
    order_data = order_resp.json()
    assert order_data["status"] == "pending"
    assert len(order_data["items"]) == 2

    # Verify stock was deducted
    p1_updated = client.get(f"/products/{p1['id']}").json()
    p2_updated = client.get(f"/products/{p2['id']}").json()
    assert p1_updated["stock"] == initial_stock_p1 - 1
    assert p2_updated["stock"] == initial_stock_p2 - 2

    # Verify cart is now empty
    cart_after = client.get("/cart", headers=buyer_headers).json()
    assert len(cart_after["items"]) == 0


def test_order_status_progression_cannot_skip(client, buyer_headers, seller_headers):
    prods = client.get("/products").json()
    order_resp = client.post("/orders/buy-now", headers=buyer_headers, json={
        "product_id": prods[0]["id"],
        "quantity": 1,
        "shipping_address": "Pokhara, Nepal",
        "destination_country": "Nepal"
    })
    order_id = order_resp.json()["id"]

    # Attempt to skip directly to shipped (from pending) -> 400
    skip_resp = client.patch(f"/orders/{order_id}/status", headers=seller_headers, json={"status": "shipped"})
    assert skip_resp.status_code == 400
    assert "cannot skip" in skip_resp.json()["detail"].lower()

    # Legitimate transition: pending -> confirmed
    conf_resp = client.patch(f"/orders/{order_id}/status", headers=seller_headers, json={"status": "confirmed"})
    assert conf_resp.status_code == 200
    assert conf_resp.json()["status"] == "confirmed"

    # Next: confirmed -> shipped
    ship_resp = client.patch(f"/orders/{order_id}/status", headers=seller_headers, json={"status": "shipped"})
    assert ship_resp.status_code == 200
    assert ship_resp.json()["status"] == "shipped"

    # Next: shipped -> delivered
    deliv_resp = client.patch(f"/orders/{order_id}/status", headers=seller_headers, json={"status": "delivered"})
    assert deliv_resp.status_code == 200
    assert deliv_resp.json()["status"] == "delivered"


def test_cancel_order_restores_stock(client, buyer_headers):
    prods = client.get("/products").json()
    prod = prods[0]
    stock_before = prod["stock"]

    # Buy now
    order_resp = client.post("/orders/buy-now", headers=buyer_headers, json={
        "product_id": prod["id"],
        "quantity": 2,
        "shipping_address": "Lalitpur, Nepal",
        "destination_country": "Nepal"
    })
    order_id = order_resp.json()["id"]

    # Verify stock deducted
    assert client.get(f"/products/{prod['id']}").json()["stock"] == stock_before - 2

    # Cancel order while pending
    cancel_resp = client.patch(f"/orders/{order_id}/cancel", headers=buyer_headers)
    assert cancel_resp.status_code == 200

    # Stock should be restored
    assert client.get(f"/products/{prod['id']}").json()["stock"] == stock_before


def test_cannot_cancel_confirmed_order(client, buyer_headers, seller_headers):
    prods = client.get("/products").json()
    order_resp = client.post("/orders/buy-now", headers=buyer_headers, json={
        "product_id": prods[0]["id"],
        "quantity": 1,
        "shipping_address": "Bhaktapur, Nepal",
        "destination_country": "Nepal"
    })
    order_id = order_resp.json()["id"]

    # Seller confirms order
    client.patch(f"/orders/{order_id}/status", headers=seller_headers, json={"status": "confirmed"})

    # Buyer attempts to cancel confirmed order -> 400
    cancel_resp = client.patch(f"/orders/{order_id}/cancel", headers=buyer_headers)
    assert cancel_resp.status_code == 400
    assert "only 'pending' orders can be cancelled" in cancel_resp.json()["detail"].lower()
