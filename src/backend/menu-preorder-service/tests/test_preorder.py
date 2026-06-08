import pytest
from uuid import uuid4, UUID
from unittest.mock import patch
from fastapi import status
from app.menu.models import Menu, MenuCategory
from app.preorder.models import Preorder, PreorderItem, PreorderStatus

def test_list_all_preorders_as_admin(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.admin

    preorder = Preorder(
        user_id=UUID("11111111-1111-1111-1111-111111111111"),
        customer_name="alice",
        total_price=15000.0,
        status=PreorderStatus.PENDING,
    )
    session.add(preorder)
    session.commit()

    response = client.get("/preorders/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["total_price"] == 15000.0
    assert data[0]["customer_name"] == "alice"

def test_list_all_preorders_as_user_forbidden(client, mock_auth_service):
    mock_auth_service.current_user = mock_auth_service.user
    response = client.get("/preorders/")
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_list_user_preorders(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.user
    user_id = mock_auth_service.user["user_id"]

    p1 = Preorder(user_id=user_id, customer_name="bob", total_price=10000.0, status=PreorderStatus.PENDING)
    p2 = Preorder(user_id=uuid4(), customer_name="other", total_price=20000.0, status=PreorderStatus.PENDING)

    session.add_all([p1, p2])
    session.commit()

    response = client.get("/preorders/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["total_price"] == 10000.0
    assert data[0]["customer_name"] == "bob"

def test_get_preorder_by_id(client, session):
    preorder = Preorder(
        user_id=uuid4(),
        total_price=12000.0,
        status=PreorderStatus.CONFIRMED
    )
    session.add(preorder)
    session.commit()
    session.refresh(preorder)
    
    response = client.get(f"/preorders/{preorder.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["total_price"] == 12000.0
    assert data["status"] == "confirmed"

def test_get_preorder_not_found(client):
    response = client.get(f"/preorders/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@patch("app.preorder.router.fetch_current_username", return_value="testuser")
@patch("app.preorder.router.register_queue_for_preorder")
def test_create_preorder_success(mock_register, mock_fetch_name, client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.user

    mock_register.return_value = {
        "queue_number": 5,
        "id": "55555555-5555-5555-5555-555555555555",
        "position": 2,
        "estimated_time": "15 minutes",
        "status": "waiting",
    }

    menu_item = Menu(name="Nasi Uduk", price=10000.0, category=MenuCategory.MAKANAN, is_available=True, is_deleted=False)
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)

    payload = {
        "notes": "Pakai sendok",
        "items": [{"menu_item_id": str(menu_item.id), "quantity": 3}],
    }

    response = client.post("/preorders/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()["data"]

    assert data["total_price"] == 30000.0          # 3 * 10000.0
    assert data["status"] == "pending"
    assert data["notes"] == "Pakai sendok"
    assert data["customer_name"] == "testuser"
    assert data["queue"]["queue_number"] == 5
    assert len(data["items"]) == 1
    assert data["items"][0]["subtotal"] == 30000.0


@patch("app.preorder.router.fetch_current_username", return_value=None)
@patch("app.preorder.router.register_queue_for_preorder")
def test_create_preorder_customer_name_none_when_user_service_unavailable(
    mock_register, mock_fetch_name, client, mock_auth_service, session
):
    """customer_name falls back to None gracefully when user-service is unreachable."""
    mock_auth_service.current_user = mock_auth_service.user

    mock_register.return_value = {
        "queue_number": 1,
        "id": str(uuid4()),
        "position": 1,
        "estimated_time": None,
        "status": "waiting",
    }

    menu_item = Menu(name="Es Teh", price=5000.0, category=MenuCategory.MINUMAN, is_available=True, is_deleted=False)
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)

    payload = {"items": [{"menu_item_id": str(menu_item.id), "quantity": 1}]}

    response = client.post("/preorders/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["customer_name"] is None

def test_create_preorder_empty_items(client, mock_auth_service):
    mock_auth_service.current_user = mock_auth_service.user
    payload = {
        "notes": "No items",
        "items": []
    }
    response = client.post("/preorders/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "at least one item" in response.json()["message"]

def test_create_preorder_menu_not_found(client, mock_auth_service):
    mock_auth_service.current_user = mock_auth_service.user
    payload = {
        "items": [
            {"menu_item_id": str(uuid4()), "quantity": 1}
        ]
    }
    response = client.post("/preorders/", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["message"]

def test_create_preorder_menu_unavailable(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.user
    menu_item = Menu(name="Es Jeruk", price=6000.0, category=MenuCategory.MINUMAN, is_available=False, is_deleted=False)
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    
    payload = {
        "items": [
            {"menu_item_id": str(menu_item.id), "quantity": 1}
        ]
    }
    response = client.post("/preorders/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not available" in response.json()["message"]

def test_create_preorder_menu_deleted(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.user
    menu_item = Menu(name="Kopi", price=5000.0, category=MenuCategory.MINUMAN, is_available=True, is_deleted=True)
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    
    payload = {
        "items": [
            {"menu_item_id": str(menu_item.id), "quantity": 1}
        ]
    }
    response = client.post("/preorders/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "deleted" in response.json()["message"]

def test_update_preorder_as_admin(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.admin
    preorder = Preorder(
        user_id=uuid4(),
        total_price=10000.0,
        status=PreorderStatus.PENDING
    )
    session.add(preorder)
    session.commit()
    session.refresh(preorder)
    
    payload = {
        "status": "confirmed",
        "queue": {"queue_number": 12, "status": "active"}
    }
    response = client.patch(f"/preorders/{preorder.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["status"] == "confirmed"
    assert data["queue"]["queue_number"] == 12

def test_cancel_preorder_success(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.user
    user_id = mock_auth_service.user["user_id"]
    
    preorder = Preorder(
        user_id=user_id,
        total_price=10000.0,
        status=PreorderStatus.PENDING
    )
    session.add(preorder)
    session.commit()
    session.refresh(preorder)
    
    response = client.patch(f"/preorders/{preorder.id}/cancel")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["status"] == "cancelled"

def test_cancel_preorder_already_confirmed_fails(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.user
    user_id = mock_auth_service.user["user_id"]
    
    preorder = Preorder(
        user_id=user_id,
        total_price=10000.0,
        status=PreorderStatus.CONFIRMED
    )
    session.add(preorder)
    session.commit()
    session.refresh(preorder)
    
    response = client.patch(f"/preorders/{preorder.id}/cancel")
    # Cancel constraint raises 404 as defined in the router
    assert response.status_code == status.HTTP_404_NOT_FOUND
