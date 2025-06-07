from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models, schemas
from ..auth import get_current_active_user
from ..database import get_db

router = APIRouter(
    prefix="/orders",
    tags=["Charging Orders"],
)


@router.get("/", response_model=List[schemas.ChargingOrder])
async def get_user_orders(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve all charging orders for the currently authenticated user.
    """
    orders = await crud.get_orders_by_user(db, user_id=current_user.user_id, skip=skip, limit=limit)
    # Eagerly load the 'request' relationship for each order to prevent serialization issues
    for order in orders:
        await db.refresh(order, attribute_names=["request"])
    return orders


@router.get("/{order_id}", response_model=schemas.ChargingOrder)
async def get_order_details(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Retrieve the details of a specific charging order.
    Ensures that a user can only access their own orders.
    """
    order = await crud.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this order"
        )

    # Also eager load the request here for consistency
    await db.refresh(order, attribute_names=["request"])
    return order
