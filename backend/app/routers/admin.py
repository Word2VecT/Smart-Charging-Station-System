from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models, schemas
from ..database import get_db
from ..services.config_service import SchedulingStrategy, config_service
from ..services.pile_simulator_service import pile_simulator_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    # dependencies=[Depends(get_current_active_admin_user)] # In a real app, secure this
)


@router.post("/piles/setup", status_code=status.HTTP_204_NO_CONTENT)
async def setup_charging_piles(pile_setup: schemas.PileSetup, db: AsyncSession = Depends(get_db)):
    """
    (Admin) Set the number of fast and trickle charging piles.
    This will delete all existing piles and related data.
    This can only be done when all piles are available.
    """
    piles = await crud.get_piles(db, limit=1000)  # get all piles
    if any(pile.status != models.PileStatus.AVAILABLE for pile in piles):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot set up piles unless all are available.",
        )

    await crud.reset_charging_piles(db, fast_piles=pile_setup.fast_piles, trickle_piles=pile_setup.trickle_piles)
    return


@router.get("/piles", response_model=List[schemas.ChargingPile])
async def list_charging_piles(db: AsyncSession = Depends(get_db)):
    """
    (Admin) Get a list of all charging piles and their current status.
    """
    piles = await crud.get_piles(db, limit=100)
    return piles


@router.get("/dashboard", response_model=schemas.DashboardData)
async def get_dashboard_data(db: AsyncSession = Depends(get_db)):
    """
    (Admin) Get comprehensive dashboard data including pile statistics and current vehicles.
    """
    # 获取所有充电桩
    piles = await crud.get_piles(db, limit=100)

    # 获取所有充电桩的统计数据
    all_stats = await crud.get_all_pile_statistics(db)

    # 组合充电桩和统计数据
    piles_with_stats = []
    for pile in piles:
        stats = all_stats.get(
            pile.pile_id,
            {
                "pile_id": pile.pile_id,
                "total_charges": 0,
                "total_charging_duration_seconds": 0,
                "total_energy_consumed_kwh": 0.0,
            },
        )

        pile_with_stats = schemas.PileWithStatistics(
            pile_id=pile.pile_id,
            pile_code=pile.pile_code,
            type=pile.type,
            status=pile.status,
            power_rate=pile.power_rate,
            statistics=schemas.PileStatistics(**stats),
        )
        piles_with_stats.append(pile_with_stats)

    # 获取当前正在充电和排队的车辆
    current_vehicles_data = await crud.get_current_charging_vehicles(db)
    current_vehicles = [schemas.CurrentVehicle(**vehicle) for vehicle in current_vehicles_data]

    return schemas.DashboardData(piles=piles_with_stats, current_vehicles=current_vehicles)


@router.get("/piles/{pile_id}/statistics", response_model=schemas.PileStatistics)
async def get_pile_statistics(pile_id: int, db: AsyncSession = Depends(get_db)):
    """
    (Admin) Get statistics for a specific charging pile.
    """
    # 验证充电桩是否存在
    pile = await crud.get_pile(db, pile_id)
    if not pile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Charging pile not found")

    stats = await crud.get_pile_statistics(db, pile_id)
    return schemas.PileStatistics(**stats)


@router.get("/vehicles/current", response_model=List[schemas.CurrentVehicle])
async def get_current_vehicles(db: AsyncSession = Depends(get_db)):
    """
    (Admin) Get information about currently charging and waiting vehicles.
    """
    vehicles_data = await crud.get_current_charging_vehicles(db)
    return [schemas.CurrentVehicle(**vehicle) for vehicle in vehicles_data]


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


@router.get("/scheduling-strategy", response_model=schemas.SchedulingStrategy)
async def get_scheduling_strategy():
    """
    Get the current scheduling strategy.
    """
    return {"strategy": config_service.scheduling_strategy.value}


@router.put("/scheduling-strategy", response_model=schemas.SchedulingStrategy)
async def set_scheduling_strategy(strategy_update: schemas.SchedulingStrategyUpdate):
    """
    Set the new scheduling strategy.
    """
    try:
        new_strategy = SchedulingStrategy(strategy_update.strategy)
        config_service.set_scheduling_strategy(new_strategy)
        return {"strategy": config_service.scheduling_strategy.value}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid strategy value")
