import pytest


def test_cart_lifecycle(client, buyer_headers):
    # Ensure cart is initially empty
    client.delete("/cart", headers=buyer_headers)

    prods = client.get("/products").json()
    test_prod = prods[0]
    prod_id = test_prod["id"]

    # 1. Add item to cart
    add_resp = client.post("/cart", headers=buyer_headers, json={"product_id": prod_id, "quantity": 1})
    assert add_resp.status_code == 201
    item_id = add_resp.json()["id"]

    # 2. Add same product merges quantity
    merge_resp = client.post("/cart", headers=buyer_headers, json={"product_id": prod_id, "quantity": 1})
    assert merge_resp.status_code == 201
    assert merge_resp.json()["quantity"] == 2

    # 3. View cart summary
    cart_resp = client.get("/cart", headers=buyer_headers)
    assert cart_resp.status_code == 200
    cart_data = cart_resp.json()
    assert len(cart_data["items"]) == 1
    assert cart_data["items"][0]["quantity"] == 2
    assert cart_data["total"] == round(test_prod["price"] * 2, 2)

    # 4. Update quantity
    update_resp = client.put(f"/cart/{item_id}", headers=buyer_headers, json={"quantity": 3})
    assert update_resp.status_code == 200
    assert update_resp.json()["quantity"] == 3

    # 5. Remove single item
    del_item_resp = client.delete(f"/cart/{item_id}", headers=buyer_headers)
    assert del_item_resp.status_code == 200

    # Cart is now empty
    empty_resp = client.get("/cart", headers=buyer_headers)
    assert len(empty_resp.json()["items"]) == 0


def test_cart_exceeding_stock_rejected(client, buyer_headers):
    client.delete("/cart", headers=buyer_headers)
    prods = client.get("/products").json()
    test_prod = prods[0]
    stock = test_prod["stock"]

    # Adding more than stock fails
    resp = client.post("/cart", headers=buyer_headers, json={
        "product_id": test_prod["id"],
        "quantity": stock + 10
    })
    assert resp.status_code == 400
    assert "exceeds available stock" in resp.json()["detail"].lower()


def test_clear_cart(client, buyer_headers):
    prods = client.get("/products").json()
    client.post("/cart", headers=buyer_headers, json={"product_id": prods[0]["id"], "quantity": 1})
    client.post("/cart", headers=buyer_headers, json={"product_id": prods[1]["id"], "quantity": 1})

    clear_resp = client.delete("/cart", headers=buyer_headers)
    assert clear_resp.status_code == 200

    cart = client.get("/cart", headers=buyer_headers).json()
    assert len(cart["items"]) == 0
