import uuid

import pytest


def _assert_envelope(payload):
    assert set(payload.keys()) == {"success", "data", "message"}


def _create_settings(client, **overrides):
    body = {
        "prefix": "A",
        "grace_period_mins": 5,
        "avg_serve_time_mins": 4,
        "max_queue_per_day": 100,
        "created_by": str(uuid.uuid4()),
        "is_queue_open": True,
        "open_time": "00:00:00",
        "close_time": "23:59:59",
    }
    body.update(overrides)
    return client.post("/queue-settings", json=body)


@pytest.fixture(name="ready_client")
def ready_client_fixture(client, seed_statuses):
    _create_settings(client)
    return client


def test_create_queue_returns_201_envelope(ready_client):
    resp = ready_client.post("/queues", json={"customer_id": str(uuid.uuid4())})
    assert resp.status_code == 201
    body = resp.json()
    _assert_envelope(body)
    assert body["success"] is True
    assert body["data"]["status_name"] == "waiting"


def test_full_happy_flow(ready_client):
    admin = str(uuid.uuid4())
    cust = str(uuid.uuid4())
    created = ready_client.post("/queues", json={"customer_id": cust}).json()
    qid = created["data"]["id"]

    ci = ready_client.post(f"/queues/{qid}/check-in", json={})
    assert ci.status_code == 200
    assert ci.json()["data"]["is_checked_in"] is True

    called = ready_client.post("/queues/call-next", json={"admin_id": admin})
    assert called.status_code == 200
    assert called.json()["data"]["status_name"] == "called"

    served = ready_client.post(f"/queues/{qid}/serve", json={"admin_id": admin})
    assert served.status_code == 200
    assert served.json()["data"]["status_name"] == "served"


def test_list_queues_and_filters(ready_client):
    ready_client.post("/queues", json={"customer_id": str(uuid.uuid4())})
    ready_client.post("/queues", json={"customer_id": str(uuid.uuid4())})
    resp = ready_client.get("/queues", params={"queue_date": "2026-06-08"})
    # default queue_date is today; filtering by a different date -> may be empty
    assert resp.status_code == 200
    _assert_envelope(resp.json())

    all_resp = ready_client.get("/queues")
    assert all_resp.status_code == 200
    assert len(all_resp.json()["data"]) == 2

    limited = ready_client.get("/queues", params={"limit": 1})
    assert len(limited.json()["data"]) == 1


def test_get_missing_queue_404_envelope(ready_client):
    resp = ready_client.get(f"/queues/{uuid.uuid4()}")
    assert resp.status_code == 404
    body = resp.json()
    _assert_envelope(body)
    assert body["success"] is False
    assert body["message"] == "Queue not found"


def test_serve_waiting_409_envelope(ready_client):
    created = ready_client.post(
        "/queues", json={"customer_id": str(uuid.uuid4())}
    ).json()
    qid = created["data"]["id"]
    resp = ready_client.post(f"/queues/{qid}/serve", json={"admin_id": str(uuid.uuid4())})
    assert resp.status_code == 409
    assert resp.json()["success"] is False


def test_call_next_no_queue_404(ready_client):
    resp = ready_client.post("/queues/call-next", json={"admin_id": str(uuid.uuid4())})
    assert resp.status_code == 404
    assert resp.json()["message"] == "There is no waiting queue to call"


def test_skip_requeue_cancel_flow(ready_client):
    admin = str(uuid.uuid4())
    created = ready_client.post(
        "/queues", json={"customer_id": str(uuid.uuid4())}
    ).json()
    qid = created["data"]["id"]
    ready_client.post("/queues/call-next", json={"admin_id": admin})
    skip = ready_client.post(
        f"/queues/{qid}/skip", json={"admin_id": admin, "trigger_type": "admin"}
    )
    assert skip.json()["data"]["status_name"] == "skipped"
    rq = ready_client.post(f"/queues/{qid}/requeue", json={"admin_id": admin})
    assert rq.status_code == 200
    assert rq.json()["data"]["is_requeued"] is True


def test_cancel_endpoint(ready_client):
    cust = str(uuid.uuid4())
    created = ready_client.post("/queues", json={"customer_id": cust}).json()
    qid = created["data"]["id"]
    resp = ready_client.post(f"/queues/{qid}/cancel", json={"customer_id": cust})
    assert resp.status_code == 200
    assert resp.json()["data"]["status_name"] == "cancelled"


def test_logs_and_notifications_endpoints(ready_client):
    created = ready_client.post(
        "/queues", json={"customer_id": str(uuid.uuid4())}
    ).json()
    qid = created["data"]["id"]
    logs = ready_client.get(f"/queues/{qid}/logs")
    assert logs.status_code == 200
    assert len(logs.json()["data"]) == 1

    notifs = ready_client.get(f"/queues/{qid}/notifications")
    assert notifs.status_code == 200
    assert notifs.json()["data"][0]["notification_type"] == "confirmation"
