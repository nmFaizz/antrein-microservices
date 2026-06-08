import uuid
from datetime import datetime, timedelta, timezone

import pytest
import jwt
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.lib.config import settings


def _mint_token(user_id: str, role: str, expired: bool = False) -> str:
    """Helper to mint test JWT tokens."""
    now = datetime.now(timezone.utc)
    exp = now - timedelta(hours=1) if expired else now + timedelta(hours=1)
    payload = {
        "user_id": user_id,
        "role": role,
        "iat": now,
        "exp": exp,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def test_bearer_auth_valid_admin_token(client):
    """Valid admin token should grant access to admin endpoints."""
    token = _mint_token(str(uuid.uuid4()), "admin")
    # GET /queue-statuses requires no auth
    resp = client.get("/queue-statuses")
    assert resp.status_code == 200

    # GET /queue-statuses with valid token
    resp = client.get("/queue-statuses", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_bearer_auth_missing_token_401(unauthenticated_client):
    """Missing Bearer token should return 401."""
    # POST /queue-statuses requires admin, no token sent
    resp = unauthenticated_client.post("/queue-statuses", json={"name": "test", "color": "#000"})
    assert resp.status_code == 401
    body = resp.json()
    assert body["success"] is False
    assert "message" in body


def test_bearer_auth_invalid_token_401(unauthenticated_client):
    """Invalid token should return 401."""
    # POST /queue-statuses requires admin auth
    resp = unauthenticated_client.post("/queue-statuses", json={"name": "test", "color": "#000"}, headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 401
    body = resp.json()
    assert body["success"] is False


def test_bearer_auth_expired_token_401(unauthenticated_client):
    """Expired token should return 401."""
    token = _mint_token(str(uuid.uuid4()), "admin", expired=True)
    # POST /queue-statuses requires admin auth
    resp = unauthenticated_client.post("/queue-statuses", json={"name": "test", "color": "#000"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    body = resp.json()
    assert body["success"] is False
    assert "expired" in body["message"].lower()


def test_bearer_auth_missing_user_id_401(unauthenticated_client):
    """Token without user_id should return 401."""
    payload = {"role": "admin", "iat": datetime.now(timezone.utc), "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    # POST /queue-statuses requires admin auth
    resp = unauthenticated_client.post("/queue-statuses", json={"name": "test", "color": "#000"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    body = resp.json()
    assert "invalid" in body["message"].lower()


def test_admin_required_customer_role_403(customer_client):
    """Customer role should not access admin endpoints."""
    token = _mint_token(str(uuid.uuid4()), "customer")
    resp = customer_client.post(
        "/queue-statuses",
        json={"name": "test", "color": "#000"},
    )
    assert resp.status_code == 403
    body = resp.json()
    assert body["success"] is False
    assert "admin" in body["message"].lower()


def test_admin_required_missing_role_401(unauthenticated_client):
    """Token with missing role should be treated as non-admin."""
    payload = {
        "user_id": str(uuid.uuid4()),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    resp = unauthenticated_client.post(
        "/queue-statuses",
        json={"name": "test", "color": "#000"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403


def test_auth_error_response_envelope(unauthenticated_client):
    """Auth errors should return envelope format {success, data, message}."""
    resp = unauthenticated_client.post("/queue-statuses", json={"name": "test", "color": "#000"})
    body = resp.json()
    assert set(body.keys()) == {"success", "data", "message"}
    assert body["success"] is False
