from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models, schemas
from ..database import get_db
from ..services.pile_simulator_service import pile_simulator_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    # dependencies=[Depends(get_current_active_admin_user)] # In a real app, secure this
)


@router.get("/piles", response_model=List[schemas.ChargingPile])
async def list_charging_piles(db: AsyncSession = Depends(get_db)):
    """
    (Admin) Get a list of all charging piles and their current status.
    """
    piles = await crud.get_piles(db, limit=100)
    return piles


class PileStatusUpdate(schemas.BaseModel):
    status: models.PileStatus
    details: str = "Updated by admin"


@router.patch("/piles/{pile_id}/status", response_model=schemas.ChargingPile)
async def update_pile_status(pile_id: int, status_update: PileStatusUpdate, db: AsyncSession = Depends(get_db)):
    """
    (Admin) Manually update the status of a charging pile (e.g., set to FAULTY or OFF).
    """
    try:
        updated_pile = await pile_simulator_service.update_pile_status_from_system(
            db=db, pile_id=pile_id, new_status=status_update.status, details=status_update.details
        )
        return updated_pile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/piles/{pile_id}/logs", response_model=List[schemas.PileLog])
async def get_pile_logs(pile_id: int, db: AsyncSession = Depends(get_db)):
    """
    (Admin) Get the event logs for a specific charging pile.
    """
    logs = await crud.get_logs_for_pile(db, pile_id=pile_id)
    return logs
