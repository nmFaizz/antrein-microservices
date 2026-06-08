"""
E2E tests — jalankan SETELAH `docker compose up`.
Tidak ada mock; semua hit ke service asli.

Alur yang diuji:
  1. User register
  2. User login → dapat token
  3. Ambil daftar menu
  4. Buat preorder dengan menu yang ada
  5. Konfirmasi preorder masuk queue (queue_number ada di response)
"""
import os
import uuid

import httpx
import pytest

USER_URL = os.getenv("USER_URL", "http://localhost:8002")
ORDER_URL = os.getenv("ORDER_URL", "http://localhost:8000")
QUEUE_URL = os.getenv("QUEUE_URL", "http://localhost:8001")

# username unik per-run agar tidak bentrok dengan data lama
_RUN_ID = str(uuid.uuid4())[:8]
TEST_USERNAME = f"e2e_user_{_RUN_ID}"
TEST_PASSWORD = "e2eTestPass123"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPreorderQueueFlow:
    """Happy-path end-to-end: register → login → menu → preorder → queue."""

    # State dibagikan antar step dalam satu class instance
    token: str = ""
    menu_item: dict = {}
    preorder: dict = {}

    def test_01_register(self):
        resp = httpx.post(
            f"{USER_URL}/auth/register",
            json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        )
        assert resp.status_code == 201, f"Register gagal: {resp.text}"
        body = resp.json()
        assert body["data"]["username"] == TEST_USERNAME
        assert body["data"]["role"] in ("user", "admin")
        print(f"\n[register] user '{TEST_USERNAME}' berhasil dibuat, id={body['data']['id']}")

    def test_02_login_dapat_token(self):
        resp = httpx.post(
            f"{USER_URL}/auth/login",
            json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        )
        assert resp.status_code == 200, f"Login gagal: {resp.text}"
        body = resp.json()
        token = body["data"]["access_token"]
        assert token, "access_token kosong"
        assert body["data"]["token_type"] == "bearer"
        TestPreorderQueueFlow.token = token
        print(f"\n[login] token diterima (panjang={len(token)})")

    def test_03_ambil_menu_tersedia(self):
        assert TestPreorderQueueFlow.token, "Butuh token dari test_02"
        resp = httpx.get(
            f"{ORDER_URL}/menu/",
            headers=auth_header(TestPreorderQueueFlow.token),
        )
        assert resp.status_code == 200, f"Get menu gagal: {resp.text}"
        menus = resp.json()["data"]
        assert isinstance(menus, list) and len(menus) > 0, (
            "Tidak ada menu di database. Tambahkan setidaknya satu menu dulu."
        )

        # Pilih menu yang tersedia dan belum dihapus
        available = [m for m in menus if m.get("is_available") and not m.get("is_deleted")]
        assert available, "Tidak ada menu yang available. Set is_available=true pada salah satu menu."

        TestPreorderQueueFlow.menu_item = available[0]
        print(
            f"\n[menu] dipilih: '{TestPreorderQueueFlow.menu_item['name']}' "
            f"(id={TestPreorderQueueFlow.menu_item['id']}, "
            f"harga={TestPreorderQueueFlow.menu_item['price']})"
        )

    def test_04_buat_preorder(self):
        assert TestPreorderQueueFlow.token, "Butuh token dari test_02"
        assert TestPreorderQueueFlow.menu_item, "Butuh menu dari test_03"

        menu = TestPreorderQueueFlow.menu_item
        payload = {
            "items": [
                {"menu_item_id": menu["id"], "quantity": 2}
            ],
            "notes": "E2E test order",
        }
        resp = httpx.post(
            f"{ORDER_URL}/preorders/",
            json=payload,
            headers=auth_header(TestPreorderQueueFlow.token),
            timeout=15.0,
        )
        assert resp.status_code == 201, f"Buat preorder gagal: {resp.text}"
        preorder = resp.json()["data"]

        # Konfirmasi item sesuai menu yang dipilih
        assert len(preorder["items"]) == 1
        assert str(preorder["items"][0]["menu_item_id"]) == menu["id"]
        assert preorder["items"][0]["quantity"] == 2

        expected_subtotal = menu["price"] * 2
        assert preorder["items"][0]["subtotal"] == pytest.approx(expected_subtotal), (
            f"Subtotal tidak sesuai: {preorder['items'][0]['subtotal']} != {expected_subtotal}"
        )
        assert preorder["total_price"] == pytest.approx(expected_subtotal)
        assert preorder["status"] == "pending"

        TestPreorderQueueFlow.preorder = preorder
        print(
            f"\n[preorder] id={preorder['id']}, "
            f"total={preorder['total_price']}, status={preorder['status']}"
        )

    def test_05_preorder_masuk_queue(self):
        assert TestPreorderQueueFlow.preorder, "Butuh preorder dari test_04"
        preorder = TestPreorderQueueFlow.preorder

        queue = preorder.get("queue")
        assert queue is not None, (
            "Field 'queue' kosong di response preorder. "
            "Queue service mungkin tidak jalan atau koneksi gagal."
        )

        # Konfirmasi field queue yang penting
        assert queue.get("queue_number") is not None, "queue_number tidak ada"
        assert queue.get("id") is not None, "queue id tidak ada"
        assert queue.get("status") is not None, "queue status tidak ada"

        print(
            f"\n[queue] MASUK ✓ — "
            f"queue_number={queue['queue_number']}, "
            f"queue_id={queue['id']}, "
            f"status={queue['status']}, "
            f"position={queue.get('position')}, "
            f"estimated_time={queue.get('estimated_time')}"
        )

        # Konfirmasi queue juga bisa diakses langsung dari queue-service
        queue_resp = httpx.get(
            f"{QUEUE_URL}/queues/{queue['id']}",
            headers=auth_header(TestPreorderQueueFlow.token),
        )
        assert queue_resp.status_code == 200, (
            f"Queue tidak ditemukan di queue-service: {queue_resp.text}"
        )
        queue_data = queue_resp.json()["data"]
        assert str(queue_data["preorder_id"]) == preorder["id"], (
            f"preorder_id di queue tidak cocok: {queue_data['preorder_id']} != {preorder['id']}"
        )
        print(
            f"[queue] konfirmasi dari queue-service ✓ — "
            f"preorder_id={queue_data['preorder_id']}"
        )


# ---------------------------------------------------------------------------
# Negative / edge cases
# ---------------------------------------------------------------------------

class TestPreorderValidation:
    """Pastikan validasi berjalan saat input salah."""

    token: str = ""

    @classmethod
    def setup_class(cls):
        """Register + login user baru untuk test ini."""
        uname = f"e2e_val_{str(uuid.uuid4())[:8]}"
        httpx.post(
            f"{USER_URL}/auth/register",
            json={"username": uname, "password": TEST_PASSWORD},
        )
        login = httpx.post(
            f"{USER_URL}/auth/login",
            json={"username": uname, "password": TEST_PASSWORD},
        )
        cls.token = login.json()["data"]["access_token"]

    def test_preorder_tanpa_item_ditolak(self):
        resp = httpx.post(
            f"{ORDER_URL}/preorders/",
            json={"items": []},
            headers=auth_header(self.token),
        )
        assert resp.status_code == 400, f"Seharusnya 400, dapat: {resp.status_code}"

    def test_preorder_menu_tidak_ada_ditolak(self):
        resp = httpx.post(
            f"{ORDER_URL}/preorders/",
            json={"items": [{"menu_item_id": str(uuid.uuid4()), "quantity": 1}]},
            headers=auth_header(self.token),
        )
        assert resp.status_code == 404, f"Seharusnya 404, dapat: {resp.status_code}"

    def test_login_password_salah(self):
        resp = httpx.post(
            f"{USER_URL}/auth/login",
            json={"username": TEST_USERNAME, "password": "wrong_password"},
        )
        assert resp.status_code in (401, 400, 403), (
            f"Login dengan password salah seharusnya gagal, dapat: {resp.status_code}"
        )

    def test_preorder_tanpa_auth_ditolak(self):
        resp = httpx.post(
            f"{ORDER_URL}/preorders/",
            json={"items": [{"menu_item_id": str(uuid.uuid4()), "quantity": 1}]},
        )
        assert resp.status_code == 401, f"Seharusnya 401, dapat: {resp.status_code}"
