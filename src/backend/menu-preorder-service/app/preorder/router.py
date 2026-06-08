from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID
import httpx

from app.db.database import get_session
from app.db.config import settings
from app.preorder.models import Preorder, PreorderResponse, PreorderCreate, PreorderUpdate, PreorderItem, PreorderStatus, PreorderItemCreate
from app.menu.models import Menu
from app.auth.dependencies import get_current_user, require_admin
from app.core.response import APIResponse, ok

router = APIRouter(prefix="/preorders", tags=["Preorders"])

@router.get("/", response_model=APIResponse[List[PreorderResponse]])
def list_preorders(session: Session = Depends(get_session), current_user = Depends(require_admin)):
    """
    List all preorders (admin).
    """
    preorders = session.exec(select(Preorder)).all()
    return ok(preorders, "Preorders retrieved successfully")

@router.get("/me", response_model=APIResponse[List[PreorderResponse]])
def list_user_preorders(session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    List preorders for the current user.
    """
    preorders = session.exec(select(Preorder).where(Preorder.user_id == current_user["user_id"])).all()
    return ok(preorders, "Preorders retrieved successfully")

@router.get("/{preorder_id}", response_model=APIResponse[PreorderResponse])
def get_preorder(preorder_id: UUID, session: Session = Depends(get_session)):
    """
    Get preorder by ID.
    """
    statement = select(Preorder).where(Preorder.id == preorder_id)
    preorder = session.exec(statement).first()
    if not preorder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preorder with ID {preorder_id} not found"
        )
    return ok(preorder, "Preorder retrieved successfully")

def validate_and_calculate_items(items: List[PreorderItemCreate], session: Session) -> tuple[float, List[PreorderItem]]:
    """Validate menu items availability and compute subtotal & total price."""
    total_price = 0.0
    preorder_items = []

    for item in items:
        statement = select(Menu).where(Menu.id == item.menu_item_id)
        menu = session.exec(statement).first()
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu with ID {item.menu_item_id} not found"
            )
        if not menu.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu '{menu.name}' is currently not available for preorder"
            )
        if menu.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu '{menu.name}' has been deleted"
            )
        
        subtotal = menu.price * item.quantity
        total_price += subtotal

        db_item = PreorderItem(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            subtotal=subtotal
        )
        preorder_items.append(db_item)
        
    return total_price, preorder_items


def register_queue_for_preorder(user_id: UUID, preorder_id: UUID) -> dict:
    """Send request to Queue Service to register queue for the preorder."""
    try:
        response = httpx.post(
            f"{settings.QUEUE_SERVICE_URL}/queues",
            json={
                "customer_id": str(user_id),
                "preorder_id": str(preorder_id)
            },
            timeout=10.0
        )
        if response.status_code == 201:
            queue_data = response.json().get("data", {})
            return {
                "queue_number": queue_data.get("queue_number"),
                "id": queue_data.get("id"),
                "position": queue_data.get("current_position"),
                "estimated_time": queue_data.get("estimated_time"),
                "status": queue_data.get("status_name")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create queue. Queue service returned status {response.status_code}: {response.text}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Queue service is unavailable: {str(e)}"
        )

@router.post("/", response_model=APIResponse[PreorderResponse], status_code=status.HTTP_201_CREATED)
def create_preorder(preorder_in: PreorderCreate, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Create a new preorder.
    """
    if not preorder_in.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preorder must contain at least one item"
        )

    # 1. Validate menu & calculate pricing
    total_price, preorder_items = validate_and_calculate_items(preorder_in.items, session)

    # 2. Save preorder with pending status
    db_preorder = Preorder(
        user_id=current_user["user_id"],
        notes=preorder_in.notes,
        total_price=total_price,
        status=PreorderStatus.PENDING,
        items=preorder_items
    )
    session.add(db_preorder)
    session.commit()
    session.refresh(db_preorder)

    # 3. Create queue entry and assign to preorder
    queue_info = register_queue_for_preorder(db_preorder.user_id, db_preorder.id)
    db_preorder.queue = queue_info
    
    session.add(db_preorder)
    session.commit()
    session.refresh(db_preorder)
    return ok(db_preorder, "Preorder created successfully")

@router.patch("/{preorder_id}", response_model=APIResponse[PreorderResponse])
def update_preorder(preorder_id: UUID, preorder_in: PreorderUpdate, session: Session = Depends(get_session), current_user = Depends(require_admin)):
    """
    Update preorder (admin).
    """
    statement = select(Preorder).where(Preorder.id == preorder_id)
    db_preorder = session.exec(statement).first()
    if not db_preorder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preorder with ID {preorder_id} not found"
        )
    
    if preorder_in.status is not None:
        db_preorder.status = preorder_in.status

    if preorder_in.queue is not None:
        db_preorder.queue = preorder_in.queue
        
    session.commit()
    session.refresh(db_preorder)
    return ok(db_preorder, "Preorder updated successfully")

@router.patch("/{preorder_id}/cancel", response_model=APIResponse[PreorderResponse])
def cancel_preorder(preorder_id: UUID, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Cancel a preorder.
    """
    statement = select(Preorder).where(Preorder.id == preorder_id, Preorder.user_id == current_user["user_id"], Preorder.status != PreorderStatus.CANCELLED, Preorder.status != PreorderStatus.CONFIRMED)
    db_preorder = session.exec(statement).first()
    if not db_preorder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preorder with ID {preorder_id} not found"
        )
    db_preorder.status = PreorderStatus.CANCELLED
    session.add(db_preorder)
    session.commit()
    session.refresh(db_preorder)
    return ok(db_preorder, "Preorder cancelled successfully")
