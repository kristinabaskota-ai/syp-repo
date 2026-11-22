import pytest


def test_admin_reports_metrics(client, admin_headers, buyer_headers, seller_headers):
    # Ensure at least one completed purchase and one cancelled order
    prods = client.get("/products").json()

    # Valid purchase
    order1 = client.post("/orders/buy-now", headers=buyer_headers, json={
        "product_id": prods[0]["id"],
        "quantity": 1,
        "shipping_address": "Kathmandu",
        "destination_country": "Nepal"
    }).json()

    # Purchase to cancel
    order2 = client.post("/orders/buy-now", headers=buyer_headers, json={
        "product_id": prods[1]["id"],
        "quantity": 1,
        "shipping_address": "Kathmandu",
        "destination_country": "Nepal"
    }).json()
    client.patch(f"/orders/{order2['id']}/cancel", headers=buyer_headers)

    # Fetch admin report
    resp = client.get("/reports", headers=admin_headers)
    assert resp.status_code == 200
    report = resp.json()

    # Total sales must be positive and exclude order2
    assert report["total_sales"] >= order1["total"]

    # Orders by status breakdown
    assert "pending" in report["orders_by_status"]
    assert "cancelled" in report["orders_by_status"]
    assert report["orders_by_status"]["cancelled"] >= 1

    # Users by role breakdown
    assert report["users_by_role"]["admin"] >= 1
    assert report["users_by_role"]["seller"] >= 1
    assert report["users_by_role"]["buyer"] >= 1

    # Low stock count
    assert report["low_stock_count"] >= 0
    assert isinstance(report["low_stock_products"], list)
