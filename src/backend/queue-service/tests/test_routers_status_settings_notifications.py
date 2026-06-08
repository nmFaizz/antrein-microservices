import uuid


def _settings_body(**overrides):
    body = {
        "prefix": "A",
        "grace_period_mins": 5,
        "avg_serve_time_mins": 4,
        "max_queue_per_day": 100,
        "created_by": str(uuid.uuid4()),
    }
    body.update(overrides)
    return body


# ------------------------- queue statuses ------------------------- #
def test_status_crud(client, seed_statuses):
    listed = client.get("/queue-statuses")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 6

    created = client.post(
        "/queue-statuses", json={"name": "vip", "color": "#FFD700"}
    )
    assert created.status_code == 201
    cid = created.json()["data"]["id"]

    got = client.get(f"/queue-statuses/{cid}")
    assert got.json()["data"]["name"] == "vip"

    patched = client.patch(f"/queue-statuses/{cid}", json={"color": "#FFAA00"})
    assert patched.json()["data"]["color"] == "#FFAA00"

    deleted = client.delete(f"/queue-statuses/{cid}")
    assert deleted.status_code == 200
    assert deleted.json()["success"] is True


def test_status_delete_default_conflict(client, seed_statuses):
    waiting_id = next(
        s["id"]
        for s in client.get("/queue-statuses").json()["data"]
        if s["name"] == "waiting"
    )
    resp = client.delete(f"/queue-statuses/{waiting_id}")
    assert resp.status_code == 409
    assert resp.json()["success"] is False


def test_status_get_missing_404(client, seed_statuses):
    resp = client.get(f"/queue-statuses/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_status_create_duplicate_409(client, seed_statuses):
    resp = client.post("/queue-statuses", json={"name": "waiting"})
    assert resp.status_code == 409


# ------------------------- queue settings ------------------------- #
def test_settings_get_unconfigured_409(client, seed_statuses):
    resp = client.get("/queue-settings")
    assert resp.status_code == 409
    assert resp.json()["success"] is False


def test_settings_create_get_patch(client, seed_statuses):
    created = client.post("/queue-settings", json=_settings_body())
    assert created.status_code == 201
    sid = created.json()["data"]["id"]

    got = client.get("/queue-settings")
    assert got.status_code == 200
    assert got.json()["data"]["prefix"] == "A"

    patched = client.patch(
        f"/queue-settings/{sid}", json={"is_queue_open": False}
    )
    assert patched.json()["data"]["is_queue_open"] is False


# ------------------------- notifications ------------------------- #
def test_notifications_filter(client, seed_statuses):
    client.post("/queue-settings", json=_settings_body())
    cust = str(uuid.uuid4())
    client.post("/queues", json={"customer_id": cust})

    all_notifs = client.get("/queue-notifications")
    assert all_notifs.status_code == 200
    assert len(all_notifs.json()["data"]) == 1

    by_customer = client.get(
        "/queue-notifications", params={"customer_id": cust}
    )
    assert len(by_customer.json()["data"]) == 1

    by_status = client.get("/queue-notifications", params={"status": "sent"})
    assert len(by_status.json()["data"]) == 1
