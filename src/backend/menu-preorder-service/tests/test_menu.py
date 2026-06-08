import pytest
from uuid import uuid4
from fastapi import status
from app.menu.models import Menu, MenuCategory

def test_list_menu_empty(client):
    response = client.get("/menu/")
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"] == []

def test_create_menu_as_admin(client, mock_auth_service, session):
    # Set role to admin
    mock_auth_service.current_user = mock_auth_service.admin
    
    payload = {
        "name": "Nasi Goreng",
        "description": "Nasi goreng pedas dengan telur",
        "price": 15000.0,
        "category": "makanan"
    }
    
    response = client.post("/menu/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["name"] == "Nasi Goreng"
    assert json_data["data"]["price"] == 15000.0
    assert json_data["data"]["category"] == "makanan"
    assert "id" in json_data["data"]

def test_create_menu_as_user_forbidden(client, mock_auth_service):
    # Set role to normal user
    mock_auth_service.current_user = mock_auth_service.user
    
    payload = {
        "name": "Nasi Goreng",
        "description": "Nasi goreng pedas dengan telur",
        "price": 15000.0,
        "category": "makanan"
    }
    
    response = client.post("/menu/", json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["success"] is False

def test_get_menu_by_id(client, session):
    # Seed a menu item
    menu = Menu(
        name="Es Teh",
        description="Es teh manis",
        price=5000.0,
        category=MenuCategory.MINUMAN
    )
    session.add(menu)
    session.commit()
    session.refresh(menu)
    
    response = client.get(f"/menu/{menu.id}")
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["name"] == "Es Teh"
    assert json_data["data"]["price"] == 5000.0

def test_get_menu_not_found(client):
    random_id = uuid4()
    response = client.get(f"/menu/{random_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["success"] is False

def test_list_menu_with_filters(client, session):
    # Seed menus
    m1 = Menu(name="Bakso", price=12000.0, category=MenuCategory.MAKANAN, is_available=True)
    m2 = Menu(name="Soto", price=10000.0, category=MenuCategory.MAKANAN, is_available=False)
    m3 = Menu(name="Mie Ayam", price=11000.0, category=MenuCategory.MAKANAN, is_available=True, is_deleted=True)
    
    session.add_all([m1, m2, m3])
    session.commit()
    
    # List all (excluding deleted)
    response = client.get("/menu/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert len(data) == 2  # Bakso, Soto
    
    # List only available
    response = client.get("/menu/?is_available=true")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Bakso"

    # List only unavailable
    response = client.get("/menu/?is_available=false")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Soto"

def test_update_menu(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.admin
    menu = Menu(name="Ayam Goreng", price=15000.0, category=MenuCategory.MAKANAN)
    session.add(menu)
    session.commit()
    session.refresh(menu)
    
    payload = {
        "price": 18000.0,
        "description": "Ayam goreng kremes"
    }
    response = client.patch(f"/menu/{menu.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["price"] == 18000.0
    assert data["description"] == "Ayam goreng kremes"
    assert data["name"] == "Ayam Goreng" # Should remain unchanged

def test_update_menu_availability(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.admin
    menu = Menu(name="Jus Alpukat", price=8000.0, category=MenuCategory.MINUMAN, is_available=True)
    session.add(menu)
    session.commit()
    session.refresh(menu)
    
    response = client.patch(f"/menu/{menu.id}/availability?is_available=false")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["is_available"] is False

def test_delete_menu(client, mock_auth_service, session):
    mock_auth_service.current_user = mock_auth_service.admin
    menu = Menu(name="Kopi", price=6000.0, category=MenuCategory.MINUMAN)
    session.add(menu)
    session.commit()
    session.refresh(menu)
    
    response = client.delete(f"/menu/{menu.id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Assert soft delete
    session.refresh(menu)
    assert menu.is_deleted is True
    
    # Get deleted menu should return 404
    get_response = client.get(f"/menu/{menu.id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
