from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models, schemas
from ..auth import get_current_active_user
from ..database import get_db

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=List[schemas.HistoryItem])
async def get_user_history(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Retrieve a unified history of all charging requests and orders for the current user.
    """
    # Fetch all orders and requests for the user
    orders = await crud.get_orders_by_user(db, user_id=current_user.user_id, limit=100)
    requests = await crud.get_requests_by_user(db, user_id=current_user.user_id, limit=100)

    history_items = []

    # Process orders
    for order in orders:
        # The request object might not be loaded, which is needed for charge_type
        await db.refresh(order, attribute_names=["request"])
        history_items.append(
            schemas.HistoryItem(
                item_id=order.order_id,
                item_type="ORDER",
                status="COMPLETED",
                date=order.created_at,
                requested_charge_amount=order.request.requested_charge_amount,
                actual_charge_amount=order.actual_charge_amount,
                total_fee=order.total_fee,
                charge_type=order.request.requested_charge_type,
            )
        )

    # Process requests that are not yet finished (don't have an order)
    for request in requests:
        if request.status != models.RequestStatus.FINISHED:
            history_items.append(
                schemas.HistoryItem(
                    item_id=request.request_id,
                    item_type="REQUEST",
                    status=request.status.value,
                    date=request.request_time,
                    requested_charge_amount=request.requested_charge_amount,
                    charge_type=request.requested_charge_type,
                )
            )

    # Sort the combined list by date in descending order
    history_items.sort(key=lambda item: item.date, reverse=True)

    return history_items


@router.get("/{order_id}", response_model=schemas.OrderDetail)
async def get_order_details(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Retrieve the detailed information for a specific order.
    """
    order = await crud.get_order_details(db, order_id=order_id, user_id=current_user.user_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or you do not have permission to view it.",
        )

    if not order.pile:
        # This case should be rare if data integrity is maintained
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve pile information for this order.",
        )

    charge_duration = order.end_time - order.start_time

    return schemas.OrderDetail(
        order_id=order.order_id,
        created_at=order.created_at,
        pile_code=order.pile.pile_code,
        actual_charge_amount=order.actual_charge_amount,
        charge_duration_seconds=int(charge_duration.total_seconds()),
        start_time=order.start_time,
        end_time=order.end_time,
        charge_fee=order.charge_fee,
        service_fee=order.service_fee,
        total_fee=order.total_fee,
    )
