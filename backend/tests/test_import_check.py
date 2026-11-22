import pytest


def test_import_check_general_rules_nepal(client):
    resp = client.get("/import-check?country=Nepal")
    assert resp.status_code == 200
    data = resp.json()
    assert data["country_found"] is True
    assert data["is_banned"] is False
    assert len(data["required_documents"]) > 0
    assert any("PQPMC" in doc for doc in data["required_documents"])
    assert "Guidance only" in data["disclaimer"]


def test_import_check_cites_warning(client):
    resp = client.get("/import-check?country=United States&plant_name=Paphiopedilum Orchid")
    assert resp.status_code == 200
    data = resp.json()
    assert data["country_found"] is True
    assert data["cites_protected"] is True
    assert data["is_banned"] is False
    assert any("CITES" in doc for doc in data["required_documents"])


def test_import_check_banned_plant_united_states(client):
    resp = client.get("/import-check?country=United States&plant_name=Water Hyacinth")
    assert resp.status_code == 200
    data = resp.json()
    assert data["country_found"] is True
    assert data["is_banned"] is True


def test_import_check_banned_plant_australia(client):
    resp = client.get("/import-check?country=Australia&plant_name=Water Hyacinth")
    assert resp.status_code == 200
    data = resp.json()
    assert data["country_found"] is True
    assert data["is_banned"] is True


def test_import_check_unknown_country(client):
    resp = client.get("/import-check?country=Wakanda&plant_name=Heart Shaped Herb")
    assert resp.status_code == 200
    data = resp.json()
    assert data["country_found"] is False
    assert "No specific import regulations found" in data["notes"][0]


def test_admin_import_rules_crud(client, admin_headers):
    # Create rule
    create_resp = client.post("/import-rules", headers=admin_headers, json={
        "country": "Germany",
        "plant_name": "*",
        "required_documents": "EU Plant Passport\nPhytosanitary Certificate",
        "is_banned": False,
        "cites_protected": False,
        "notes": "EU intra-community trade regulations apply."
    })
    assert create_resp.status_code == 201
    rule_id = create_resp.json()["id"]

    # Update rule
    update_resp = client.put(f"/import-rules/{rule_id}", headers=admin_headers, json={
        "notes": "Updated EU customs directive note."
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["notes"] == "Updated EU customs directive note."

    # Delete rule
    del_resp = client.delete(f"/import-rules/{rule_id}", headers=admin_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Import rule deleted successfully."
