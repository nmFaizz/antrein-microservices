from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.db.database import get_session
from app.menu.models import Menu, MenuCreate, MenuUpdate
from app.auth.dependencies import require_admin
from app.core.response import APIResponse, ok

router = APIRouter(prefix="/menu", tags=["Menu"])

@router.get("/", response_model=APIResponse[List[Menu]])
def list_menu(is_available: bool = None, session: Session = Depends(get_session)):
    """
    List all available menus.
    """
    statement = select(Menu).where(Menu.is_deleted == False)
    if is_available is not None:
        statement = statement.where(Menu.is_available == is_available)
    menus = session.exec(statement).all()
    return ok(menus, "Menus retrieved successfully")

@router.get("/{menu_id}", response_model=APIResponse[Menu])
def get_menu(menu_id: UUID, session: Session = Depends(get_session)):
    """
    Get menu by ID.
    """
    statement = select(Menu).where(Menu.id == menu_id, Menu.is_deleted == False)
    menu = session.exec(statement).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu with ID {menu_id} not found"
        )
    return ok(menu, "Menu retrieved successfully")

@router.post("/", response_model=APIResponse[Menu], status_code=status.HTTP_201_CREATED)
def create_menu(menu_in: MenuCreate, session: Session = Depends(get_session), current_user = Depends(require_admin)):
    """
    Create a new menu item.
    """
    db_menu = Menu.model_validate(menu_in)
    session.add(db_menu)
    session.commit()
    session.refresh(db_menu)
    return ok(db_menu, "Menu created successfully")

@router.patch("/{menu_id}", response_model=APIResponse[Menu])
def update_menu(menu_id: UUID, menu_in: MenuUpdate, session: Session = Depends(get_session), current_user = Depends(require_admin)):
    """
    Update an existing menu item.
    """
    statement = select(Menu).where(Menu.id == menu_id, Menu.is_deleted == False)
    db_menu = session.exec(statement).first()
    if not db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu with ID {menu_id} not found"
        )
    
    update_data = menu_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_menu, key, value)
        
    session.add(db_menu)
    session.commit()
    session.refresh(db_menu)
    return ok(db_menu, "Menu updated successfully")

@router.patch("/{menu_id}/availability", response_model=APIResponse[Menu])
def update_menu_availability(menu_id: UUID, is_available: bool, session: Session = Depends(get_session), current_user = Depends(require_admin)):
    """
    Update the availability of a menu item (true or false).
    """
    statement = select(Menu).where(Menu.id == menu_id, Menu.is_deleted == False)
    db_menu = session.exec(statement).first()
    if not db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu with ID {menu_id} not found"
        )
    db_menu.is_available = is_available
    session.add(db_menu)
    session.commit()
    session.refresh(db_menu)
    return ok(db_menu, "Menu availability updated successfully")

@router.delete("/{menu_id}", response_model=APIResponse[None])
def delete_menu(menu_id: UUID, session: Session = Depends(get_session) , current_user = Depends(require_admin)):
    """
    Delete a menu item.
    """
    statement = select(Menu).where(Menu.id == menu_id, Menu.is_deleted == False)
    db_menu = session.exec(statement).first()
    if not db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu with ID {menu_id} not found"
        )
    db_menu.is_deleted = True
    session.add(db_menu)
    session.commit()
    return ok(None, "Menu deleted successfully")
