from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.db.database import get_session
from app.order.models import Order, OrderResponse, OrderCreate, OrderUpdate, OrderItem, OrderStatus
from app.menu.models import Menu
from app.auth.dependencies import get_current_user, require_admin
from app.core.response import APIResponse, ok

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=APIResponse[List[OrderResponse]])
def list_orders(session: Session = Depends(get_session), current_user = Depends(require_admin)):
    """
    List all orders (admin).
    """
    orders = session.exec(select(Order)).all()
    return ok(orders, "Orders retrieved successfully")

@router.get("/{order_id}", response_model=APIResponse[OrderResponse])
def get_order(order_id: UUID, session: Session = Depends(get_session)):
    """
    Get order by ID.
    """
    statement = select(Order).where(Order.id == order_id)
    order = session.exec(statement).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return ok(order, "Order retrieved successfully")

@router.post("/", response_model=APIResponse[OrderResponse], status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrderCreate, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Create a new order.
    """
    if not order_in.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )

    total_price = 0.0
    order_items = []

    for item in order_in.items:
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
                detail=f"Menu '{menu.name}' is currently not available for order"
            )
        if menu.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu '{menu.name}' has been deleted"
            )
        
        subtotal = menu.price * item.quantity
        total_price += subtotal

        db_item = OrderItem(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            subtotal=subtotal
        )
        order_items.append(db_item)

    db_order =  Order(
        user_id=current_user["user_id"],
        notes=order_in.notes,
        total_price=total_price,
        status=OrderStatus.PENDING,
        items=order_items
    )

    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return ok(db_order, "Order created successfully")

@router.patch("/{order_id}", response_model=APIResponse[OrderResponse])
def update_order(order_id: UUID, order_in: OrderUpdate, session: Session = Depends(get_session), current_user = Depends(require_admin)):
    """
    Update order (admin). Queue number given from queue service, status can be updated to "confirmed" or "cancelled".
    ```
    """
    statement = select(Order).where(Order.id == order_id)
    db_order = session.exec(statement).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    if order_in.status is not None:
        db_order.status = order_in.status
    
    if order_in.queue_number is not None:
        if db_order.status == OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Queue number cannot be set for pending orders"
            )
        db_order.queue_number = order_in.queue_number
        
    session.commit()
    session.refresh(db_order)
    return ok(db_order, "Order updated successfully")

@router.patch("/{order_id}/cancel", response_model=APIResponse[OrderResponse])
def cancel_order(order_id: UUID, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Cancel an order.
    """
    statement = select(Order).where(Order.id == order_id, Order.user_id == current_user["user_id"], Order.status != "cancelled", Order.status != "confirmed")
    db_order = session.exec(statement).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    db_order.status = OrderStatus.CANCELLED
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return ok(db_order, "Order cancelled successfully")
