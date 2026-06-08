import uuid

from app.db.session import get_db_session, get_session


def test_root_envelope(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {
        "success": True,
        "data": None,
        "message": "Welcome to the Queue Service API",
    }


def test_validation_error_envelope(client, seed_statuses):
    # preorder_id is not a valid UUID -> 422 via the RequestValidationError handler.
    resp = client.post(
        "/queues", json={"customer_id": str(uuid.uuid4()), "preorder_id": "nope"}
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert isinstance(body["data"], list)


def test_unexpected_error_envelope(client, monkeypatch):
    # Force a non-domain exception inside a route to exercise the 500 handler.
    from app.services import queue_settings_service

    def boom(self):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(
        queue_settings_service.QueueSettingsService, "get_active", boom
    )
    resp = client.get("/queue-settings")
    assert resp.status_code == 500
    body = resp.json()
    assert body["success"] is False
    assert body["message"] == "Internal server error"
    assert body["data"] is None


def test_session_generators_smoke():
    # Cover the module-level session dependency generators.
    gen = get_session()
    session = next(gen)
    assert session is not None
    gen.close()

    with get_db_session() as ctx_session:
        assert ctx_session is not None
