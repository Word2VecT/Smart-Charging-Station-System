from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import models, schemas
from .auth import get_password_hash

# Generic CRUD functions can be created, but for clarity, we'll define for each model.


# User CRUD
async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.user_id == user_id))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, password_hash=hashed_password, role=user.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# ChargingPile CRUD
async def get_pile(db: AsyncSession, pile_id: int) -> Optional[models.ChargingPile]:
    result = await db.execute(select(models.ChargingPile).filter(models.ChargingPile.pile_id == pile_id))
    return result.scalars().first()


async def get_piles(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[models.ChargingPile]:
    result = await db.execute(select(models.ChargingPile).offset(skip).limit(limit))
    return result.scalars().all()


async def create_pile(db: AsyncSession, pile: schemas.ChargingPileCreate) -> models.ChargingPile:
    db_pile = models.ChargingPile(**pile.dict())
    db.add(db_pile)
    await db.commit()
    await db.refresh(db_pile)
    return db_pile


async def update_pile_status(
    db: AsyncSession, pile_id: int, status: schemas.PileStatus
) -> Optional[models.ChargingPile]:
    db_pile = await get_pile(db, pile_id)
    if db_pile:
        db_pile.status = status
        await db.commit()
        await db.refresh(db_pile)
    return db_pile


# ChargingRequest CRUD
async def get_request(db: AsyncSession, request_id: int) -> Optional[models.ChargingRequest]:
    result = await db.execute(select(models.ChargingRequest).filter(models.ChargingRequest.request_id == request_id))
    return result.scalars().first()


async def get_requests(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.ChargingRequest]:
    result = await db.execute(select(models.ChargingRequest).offset(skip).limit(limit))
    return result.scalars().all()


async def create_request(db: AsyncSession, request: schemas.ChargingRequestCreate) -> models.ChargingRequest:
    db_request = models.ChargingRequest(**request.dict())
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)
    return db_request


async def get_user_active_request(db: AsyncSession, user_id: int) -> Optional[models.ChargingRequest]:
    """
    Finds the latest active (WAITING or CHARGING) request for a given user.
    """
    result = await db.execute(
        select(models.ChargingRequest)
        .filter(
            models.ChargingRequest.user_id == user_id,
            models.ChargingRequest.status.in_([models.RequestStatus.WAITING, models.RequestStatus.CHARGING]),
        )
        .order_by(models.ChargingRequest.request_time.desc())
    )
    return result.scalars().first()


async def get_requests_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.ChargingRequest]:
    """
    Retrieves all charging requests for a specific user.
    """
    result = await db.execute(
        select(models.ChargingRequest)
        .filter(models.ChargingRequest.user_id == user_id)
        .order_by(models.ChargingRequest.request_time.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# ChargingOrder CRUD
async def create_order(db: AsyncSession, order: schemas.ChargingOrderCreate) -> models.ChargingOrder:
    db_order = models.ChargingOrder(**order.dict())
    db.add(db_order)
    await db.flush()
    await db.refresh(db_order)
    return db_order


async def get_order(db: AsyncSession, order_id: int) -> Optional[models.ChargingOrder]:
    result = await db.execute(select(models.ChargingOrder).filter(models.ChargingOrder.order_id == order_id))
    return result.scalars().first()


async def get_orders_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.ChargingOrder]:
    result = await db.execute(
        select(models.ChargingOrder)
        .filter(models.ChargingOrder.user_id == user_id)
        .order_by(models.ChargingOrder.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# OperationalReport CRUD
async def create_report(db: AsyncSession, report: schemas.OperationalReportCreate) -> models.OperationalReport:
    db_report = models.OperationalReport(**report.dict())
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report


# PileLog CRUD
async def create_pile_log(db: AsyncSession, log: schemas.PileLogCreate) -> models.PileLog:
    db_log = models.PileLog(**log.dict())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


async def get_logs_for_pile(db: AsyncSession, pile_id: int, skip: int = 0, limit: int = 100) -> List[models.PileLog]:
    result = await db.execute(
        select(models.PileLog)
        .filter(models.PileLog.pile_id == pile_id)
        .order_by(models.PileLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
