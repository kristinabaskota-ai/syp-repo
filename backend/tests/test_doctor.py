import pytest


def test_doctor_parts_and_symptoms(client):
    parts_resp = client.get("/doctor/parts")
    assert parts_resp.status_code == 200
    parts = parts_resp.json()
    assert "leaf" in parts
    assert "stem" in parts
    assert "root" in parts
    assert "flower" in parts

    # Filter by leaf
    leaf_symptoms = client.get("/doctor/symptoms?plant_part=leaf").json()
    assert len(leaf_symptoms) > 0
    assert all(s["plant_part"] == "leaf" for s in leaf_symptoms)


def test_doctor_diagnosis_ranking_organic_first(client):
    symptoms = client.get("/doctor/symptoms?plant_part=leaf").json()
    # Find Powdery Mildew symptom which has organic, non-chemical, and chemical treatments
    mildew_symptom = [s for s in symptoms if "Powdery Mildew" in s["diagnosis"]][0]

    resp = client.post("/doctor/diagnose", json={
        "symptom_id": mildew_symptom["id"],
        "has_pets": False,
        "has_children": False,
        "plant_is_edible": False
    })
    assert resp.status_code == 200
    data = resp.json()
    treatments = data["safe_treatments"]
    assert len(treatments) >= 3

    # Verify ranking: organic before chemical
    types = [t["treatment_type"] for t in treatments]
    assert types[0] == "organic"
    assert "chemical" in types
    # Chemical must be after organic
    assert types.index("chemical") > types.index("organic")


def test_doctor_household_pet_safety_filter(client):
    symptoms = client.get("/doctor/symptoms?plant_part=leaf").json()
    mildew = [s for s in symptoms if "Powdery Mildew" in s["diagnosis"]][0]

    # Without pets
    res_no_pets = client.post("/doctor/diagnose", json={
        "symptom_id": mildew["id"],
        "has_pets": False
    }).json()

    # With pets: chemical treatment must be hidden!
    res_pets = client.post("/doctor/diagnose", json={
        "symptom_id": mildew["id"],
        "has_pets": True
    }).json()

    assert res_pets["hidden_treatments_count"] > 0
    assert len(res_pets["safe_treatments"]) < len(res_no_pets["safe_treatments"])
    # All remaining treatments must be pet_safe
    assert all(t["pet_safe"] is True for t in res_pets["safe_treatments"])
    # Systemic chemical fungicide should NOT be present
    assert not any(t["treatment_type"] == "chemical" for t in res_pets["safe_treatments"])


def test_doctor_diagnosis_links_shop_product(client):
    symptoms = client.get("/doctor/symptoms?plant_part=leaf").json()
    spider_mites = [s for s in symptoms if "Spider Mite" in s["diagnosis"]][0]

    resp = client.post("/doctor/diagnose", json={
        "symptom_id": spider_mites["id"],
        "has_pets": True
    })
    assert resp.status_code == 200
    data = resp.json()

    # Verify at least one treatment has a linked product with name and price
    linked = [t for t in data["safe_treatments"] if t["product"] is not None]
    assert len(linked) > 0
    first_linked = linked[0]["product"]
    assert first_linked["price"] > 0
    assert first_linked["stock"] > 0


def test_doctor_diagnosis_history(client, buyer_headers):
    symptoms = client.get("/doctor/symptoms?plant_part=stem").json()
    mealybug = symptoms[0]

    # Run diagnosis as authenticated buyer
    client.post("/doctor/diagnose", headers=buyer_headers, json={
        "symptom_id": mealybug["id"],
        "has_pets": True,
        "has_children": True
    })

    # Retrieve history
    hist_resp = client.get("/doctor/history", headers=buyer_headers)
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) > 0
    assert history[0]["symptom_id"] == mealybug["id"]
    assert history[0]["has_pets"] is True
    assert history[0]["has_children"] is True
