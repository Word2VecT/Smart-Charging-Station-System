import datetime as dt
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models, schemas
from ..auth import get_current_active_user
from ..database import get_db
from ..queue_manager import queue_manager
from ..services.billing_service import billing_service

router = APIRouter(
    prefix="/requests",
    tags=["Charging Requests"],
)


@router.post("/", response_model=schemas.ChargingRequest, status_code=status.HTTP_201_CREATED)
async def create_charging_request(
    request: schemas.ChargingRequestBody,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Submits a new charging request.

    - **requested_charge_type**: FAST or TRICKLE.
    - **requested_charge_amount**: The amount of charge requested in kWh.

    The user is placed in the waiting queue and assigned a queue number.
    An error is returned if the waiting area is full.
    """
    # The user_id is taken from the authentication token, not the request body.
    full_request_data = schemas.ChargingRequestCreate(
        user_id=current_user.user_id,
        requested_charge_type=request.requested_charge_type,
        requested_charge_amount=request.requested_charge_amount,
    )

    db_request, error_msg = await queue_manager.add_request_to_waiting_queue(db, full_request_data)

    if error_msg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    return db_request


@router.get("/waiting-queue", response_model=List[schemas.ChargingRequest])
async def get_waiting_queue():
    """
    Get the current list of all requests in the waiting area (both FAST and TRICKLE).
    """
    # The response_model will serialize the SQLAlchemy models correctly
    return list(queue_manager.waiting_queue_fast) + list(queue_manager.waiting_queue_trickle)


@router.get("/me/active", response_model=schemas.ChargingRequest | None)
async def get_my_active_request(
    db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_active_user)
):
    """
    Get the current user's active charging request (status WAITING or CHARGING).
    """
    active_request = await crud.get_user_active_request(db, user_id=current_user.user_id)
    return active_request


@router.get("/{request_id}", response_model=schemas.ChargingRequest)
async def get_request_status(request_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get the status of a specific charging request by its ID.
    """
    db_request = await crud.get_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return db_request


@router.post("/{request_id}/stop", response_model=schemas.ChargingOrder)
async def stop_charging_request(
    request_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_active_user)
):
    """
    Manually stops an ongoing charging session.
    Calculates the charge up to the current moment and generates a final order.
    """
    request = await crud.get_request(db, request_id)

    # Validation
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")
    if request.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only stop your own requests.")
    if request.status != models.RequestStatus.CHARGING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is not currently charging.")
    if not request.start_time or not request.assigned_pile_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Inconsistent request data: cannot stop charge."
        )

    pile = await crud.get_pile(db, request.assigned_pile_id)
    if not pile:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Associated pile not found.")

    end_time = dt.datetime.now(dt.timezone.utc)
    duration_seconds = (end_time - request.start_time).total_seconds()
    actual_charge_amount = (Decimal(duration_seconds) / Decimal(3600)) * pile.power_rate

    order = await billing_service.finish_charging_session(
        db=db, request_id=request_id, end_time=end_time, actual_charge_amount=actual_charge_amount
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create a charging order."
        )

    return order


@router.patch("/{request_id}", response_model=schemas.ChargingRequest)
async def modify_charging_request(
    request_id: int,
    update_data: schemas.ChargingRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Modify an existing charging request (only available in 'WAITING' status).
    """
    updated_request, error_msg = await queue_manager.modify_request(db, request_id, current_user.user_id, update_data)
    if error_msg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    return updated_request


@router.post("/{request_id}/cancel", response_model=schemas.ChargingRequest)
async def cancel_charging_request(
    request_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_active_user)
):
    """
    Cancel a request that is in the 'WAITING' queue.
    """
    cancelled_request, error_msg = await queue_manager.cancel_request(db, request_id, current_user.user_id)
    if error_msg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    return cancelled_request


@router.post("/fault-report/{pile_id}")
async def report_pile_fault(
    pile_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_active_user)
):
    """
    Report a fault for a charging pile. This will:
    1. Stop any ongoing charging session and generate a bill
    2. Set the pile status to FAULTY
    3. Re-queue any remaining charge amount to the front of the waiting queue
    """
    from ..services.fault_service import fault_service

    result = await fault_service.handle_pile_fault(db, pile_id)

    if result["error"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return {"message": "故障上报成功", "details": result}
