from http import HTTPStatus

def test_auth_login_ok(client, seed_admin):
    r = client.post("/auth/login", json={
        "email": "shakibadmin@local.fr",
        "password": "AdminFort123"
    })
    assert r.status_code == 200
    data = r.get_json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"

def test_missions_requires_auth(client):
    r = client.get("/missions")
    assert r.status_code in (HTTPStatus.UNAUTHORIZED, 401)

def test_full_flow_mission_resource_assign_and_release(client, auth_headers):
    # 1) Créer une ressource
    r = client.post(
        "/resources",
        json={"type": "drone", "label": "DRN-001", "status": "available", "details": "Test unit"},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.get_json()
    res = r.get_json()
    rid = res["id"]
    assert res["status"] in ("available", "AVAILABLE", "Available")

    # 2) Créer une mission
    m = client.post(
        "/missions",
        json={
            "title": "Surveillance sector 7",
            "description": "Night ops",
            "status": "planned",
            "date": "2025-11-15T20:00:00Z",
            "lat": 44.84,
            "lon": -0.57
        },
        headers=auth_headers,
    )
    assert m.status_code == 201, m.get_json()
    mission = m.get_json()
    mid = mission["id"]

    # 3) Assigner la ressource à la mission (alias /missions/<id>/assign)
    a = client.post(
        f"/missions/{mid}/assign",
        json={"resource_id": rid, "note": "Init assignment"},
        headers=auth_headers,
    )
    assert a.status_code == 201, a.get_json()
    link = a.get_json()
    assert link["mission_id"] == mid
    assert link["resource_id"] == rid

    # 4) Vérifier que la ressource passe en ASSIGNED
    rr = client.get("/resources", headers=auth_headers)
    assert rr.status_code == 200
    items = rr.get_json().get("items") or rr.get_json()
    r_after = [x for x in items if x["id"] == rid][0]
    assert r_after["status"].lower() == "assigned"

    # 5) Supprimer la mission
    d = client.delete(f"/missions/{mid}", headers=auth_headers)
    assert d.status_code == 200, d.get_json()

    # 6) Vérifier que la ressource est redevenue AVAILABLE
    rr2 = client.get("/resources", headers=auth_headers)
    assert rr2.status_code == 200
    items2 = rr2.get_json().get("items") or rr2.get_json()
    r_final = [x for x in items2 if x["id"] == rid][0]
    assert r_final["status"].lower() == "available"
