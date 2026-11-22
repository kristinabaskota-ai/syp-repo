import pytest


def test_wanted_board_flow(client, buyer_headers, seller_headers, admin_headers):
    # 1. Buyer creates wanted request
    req_resp = client.post("/wanted", headers=buyer_headers, json={
        "plant_name": "Variegated Spiritus Sancti",
        "destination_country": "Nepal",
        "details": "Looking for a healthy rooted seedling with verified pedigree."
    })
    assert req_resp.status_code == 201
    req_id = req_resp.json()["id"]
    assert req_resp.json()["status"] == "open"

    # 2. Seller makes an offer
    offer_resp = client.post(f"/wanted/{req_id}/offers", headers=seller_headers, json={
        "price": 25000.0,
        "message": "Established TC specimen in a 4-inch pot, ready for pickup."
    })
    assert offer_resp.status_code == 201
    offer1_id = offer_resp.json()["id"]

    # 3. Seller cannot make a duplicate offer on the same request
    dup_resp = client.post(f"/wanted/{req_id}/offers", headers=seller_headers, json={
        "price": 24000.0,
        "message": "Lowering my price offer."
    })
    assert dup_resp.status_code == 400
    assert "already submitted an offer" in dup_resp.json()["detail"].lower()

    # 4. Create second seller to make second offer
    client.post("/auth/register", json={
        "full_name": "Botanical Seller Two",
        "email": "seller_two@example.com",
        "password": "Password123",
        "role": "seller"
    })
    users = client.get("/users", headers=admin_headers).json()
    s2_id = [u["id"] for u in users if u["email"] == "seller_two@example.com"][0]
    client.patch(f"/users/{s2_id}/approve", headers=admin_headers, json={"is_approved": True})
    s2_tok = client.post("/auth/login", json={"email": "seller_two@example.com", "password": "Password123"}).json()["access_token"]
    s2_headers = {"Authorization": f"Bearer {s2_tok}"}

    offer2_resp = client.post(f"/wanted/{req_id}/offers", headers=s2_headers, json={
        "price": 22000.0,
        "message": "Top cutting with 2 aerial roots."
    })
    assert offer2_resp.status_code == 201
    offer2_id = offer2_resp.json()["id"]

    # 5. Buyer views offers
    offers_resp = client.get(f"/wanted/{req_id}/offers", headers=buyer_headers)
    assert offers_resp.status_code == 200
    offers = offers_resp.json()
    assert len(offers) == 2

    # 6. Buyer accepts offer 2
    accept_resp = client.post(f"/wanted/{req_id}/offers/{offer2_id}/accept", headers=buyer_headers)
    assert accept_resp.status_code == 200
    updated_req = accept_resp.json()
    assert updated_req["status"] == "fulfilled"

    # Verify offer 2 is accepted and offer 1 is rejected
    req_offers = client.get(f"/wanted/{req_id}/offers", headers=buyer_headers).json()
    o1 = [o for o in req_offers if o["id"] == offer1_id][0]
    o2 = [o for o in req_offers if o["id"] == offer2_id][0]
    assert o2["status"] == "accepted"
    assert o1["status"] == "rejected"


def test_close_wanted_request(client, buyer_headers):
    req_resp = client.post("/wanted", headers=buyer_headers, json={
        "plant_name": "Philodendron Billietiae",
        "destination_country": "Nepal",
        "details": "Orange petioles wanted."
    })
    req_id = req_resp.json()["id"]

    close_resp = client.patch(f"/wanted/{req_id}/close", headers=buyer_headers)
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "closed"
