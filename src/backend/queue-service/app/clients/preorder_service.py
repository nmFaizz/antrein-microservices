import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
import jwt

logger = logging.getLogger(__name__)


class PreorderServiceClient:
    """Client for the menu-preorder-service (queue -> preorder callback).

    Keeps the preorder's ``queue`` snapshot and ``status`` in sync as the queue
    advances. Calls are **best-effort**: any failure is logged and swallowed so
    queue operations are never blocked by preorder availability. When
    ``base_url`` is falsy the integration is disabled (every call is a no-op),
    which keeps local/dev and tests working without the preorder service.

    Authenticates by minting a short-lived admin JWT signed with the shared
    ``secret_key`` (the preorder's ``PATCH /preorders/{id}`` requires role=admin).
    """

    def __init__(
        self,
        base_url: Optional[str],
        secret_key: Optional[str],
        service_account_id: str,
        algorithm: str = "HS256",
        token_ttl_seconds: int = 300,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.secret_key = secret_key
        self.service_account_id = service_account_id
        self.algorithm = algorithm
        self.token_ttl_seconds = token_ttl_seconds
        self.timeout = timeout

    def sync(
        self,
        preorder_id: uuid.UUID,
        queue_snapshot: dict,
        status: Optional[str] = None,
    ) -> None:
        if not self.base_url:
            return

        body: dict = {"queue": queue_snapshot}
        if status is not None:
            body["status"] = status

        try:
            headers = {"Authorization": f"Bearer {self._mint_token()}"}
            response = httpx.patch(
                f"{self.base_url}/preorders/{preorder_id}",
                json=body,
                headers=headers,
                timeout=self.timeout,
            )
            if response.status_code >= 400:
                logger.warning(
                    "Preorder sync for %s returned %s: %s",
                    preorder_id,
                    response.status_code,
                    response.text,
                )
        except httpx.RequestError as exc:
            logger.warning(
                "Preorder sync for %s failed (service unavailable): %s",
                preorder_id,
                exc,
            )

    def get_preorder(
        self, preorder_id: uuid.UUID
    ) -> Optional[dict]:
        """Fetch preorder by ID (no auth required, best-effort).

        Strips the 'queue' field to avoid circular references.
        """
        if not self.base_url:
            return None

        try:
            response = httpx.get(
                f"{self.base_url}/preorders/{preorder_id}",
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json().get("data", {})
                data.pop("queue", None)  # avoid circular: preorder.queue -> queue
                return data
            return None
        except httpx.RequestError as exc:
            logger.warning(
                "Preorder fetch for %s failed (service unavailable): %s",
                preorder_id,
                exc,
            )
            return None

    def _mint_token(self) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": self.service_account_id,
            "role": "admin",
            "iat": now,
            "exp": now + timedelta(seconds=self.token_ttl_seconds),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
