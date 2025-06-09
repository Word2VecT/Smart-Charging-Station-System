from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from . import models, schemas
from .auth import get_password_hash


# ===================
# 用户相关 CRUD
# ===================
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


# ===================
# 充电桩相关 CRUD
# ===================
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


async def reset_charging_piles(db: AsyncSession, fast_piles: int, trickle_piles: int):
    """
    Deletes all existing charging piles and creates a new set of piles.
    WARNING: This will delete all related data like orders and logs due to CASCADE.
    """
    await db.execute(text(f"TRUNCATE TABLE {models.ChargingPile.__tablename__} RESTART IDENTITY CASCADE;"))

    new_piles = []
    # Create fast piles
    for i in range(1, fast_piles + 1):
        pile_code = f"F{i:03d}"
        new_piles.append(
            models.ChargingPile(
                pile_code=pile_code,
                type=models.PileType.FAST,
                status=models.PileStatus.AVAILABLE,
                power_rate=30.0,
            )
        )

    # Create trickle piles
    for i in range(1, trickle_piles + 1):
        pile_code = f"T{i:03d}"
        new_piles.append(
            models.ChargingPile(
                pile_code=pile_code,
                type=models.PileType.TRICKLE,
                status=models.PileStatus.AVAILABLE,
                power_rate=7.0,
            )
        )

    if new_piles:
        db.add_all(new_piles)

    await db.commit()


# ===================
# 请求相关 CRUD
# ===================
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
    result = await db.execute(
        select(models.ChargingRequest)
        .filter(models.ChargingRequest.user_id == user_id)
        .order_by(models.ChargingRequest.request_time.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# ===================
# 订单相关 CRUD
# ===================
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


async def get_order_details(db: AsyncSession, order_id: int, user_id: int) -> Optional[models.ChargingOrder]:
    """
    Get detailed information for a specific order, including the associated pile data.
    Ensures the order belongs to the specified user.
    """
    result = await db.execute(
        select(models.ChargingOrder)
        .options(joinedload(models.ChargingOrder.pile))
        .filter(models.ChargingOrder.order_id == order_id, models.ChargingOrder.user_id == user_id)
    )
    return result.scalars().first()


# ===================
# 报表 CRUD
# ===================
async def create_report(db: AsyncSession, report: schemas.OperationalReportCreate) -> models.OperationalReport:
    db_report = models.OperationalReport(**report.dict())
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report


# ===================
# 日志 CRUD
# ===================
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


# ===================
# 管理员相关 CRUD（修改后）
# ===================


async def get_admin_by_username(db: AsyncSession, username: str) -> Optional[models.Admin]:
    result = await db.execute(select(models.Admin).filter(models.Admin.username == username))
    return result.scalars().first()


async def create_admin(db: AsyncSession, admin: schemas.AdminCreate) -> models.Admin:
    # 直接使用明文密码存储（注意：仅用于测试或受限环境，生产环境极不推荐）
    db_admin = models.Admin(username=admin.username, password_hash=admin.password)
    db.add(db_admin)
    await db.commit()
    await db.refresh(db_admin)
    return db_admin


async def authenticate_admin(db: AsyncSession, username: str, password: str) -> Optional[models.Admin]:
    admin = await get_admin_by_username(db, username)
    if admin and admin.password_hash == password:
        return admin
    return None


# 获取所有订单（不限定 user_id）
async def get_all_orders(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.ChargingOrder]:
    result = await db.execute(
        select(models.ChargingOrder).order_by(models.ChargingOrder.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


# ===================
# 充电桩统计数据 CRUD
# ===================


async def get_pile_statistics(db: AsyncSession, pile_id: int):
    """获取单个充电桩的累计统计数据"""
    from sqlalchemy import func

    # 获取充电次数
    charging_count_result = await db.execute(
        select(func.count(models.ChargingOrder.order_id)).filter(models.ChargingOrder.pile_id == pile_id)
    )
    charging_count = charging_count_result.scalar() or 0

    # 获取累计充电时长（秒）和充电量
    duration_energy_result = await db.execute(
        select(
            func.coalesce(
                func.sum(func.extract("epoch", models.ChargingOrder.end_time - models.ChargingOrder.start_time)), 0
            ),
            func.coalesce(func.sum(models.ChargingOrder.actual_charge_amount), 0),
        ).filter(models.ChargingOrder.pile_id == pile_id)
    )
    duration_seconds, total_energy = duration_energy_result.first()

    return {
        "pile_id": pile_id,
        "total_charges": charging_count,
        "total_charging_duration_seconds": int(duration_seconds or 0),
        "total_energy_consumed_kwh": float(total_energy or 0),
    }


async def get_all_pile_statistics(db: AsyncSession):
    """获取所有充电桩的统计数据"""
    from sqlalchemy import func

    result = await db.execute(
        select(
            models.ChargingOrder.pile_id,
            func.count(models.ChargingOrder.order_id).label("total_charges"),
            func.coalesce(
                func.sum(func.extract("epoch", models.ChargingOrder.end_time - models.ChargingOrder.start_time)), 0
            ).label("total_duration_seconds"),
            func.coalesce(func.sum(models.ChargingOrder.actual_charge_amount), 0).label("total_energy"),
        ).group_by(models.ChargingOrder.pile_id)
    )

    stats_dict = {}
    for row in result:
        stats_dict[row.pile_id] = {
            "pile_id": row.pile_id,
            "total_charges": row.total_charges,
            "total_charging_duration_seconds": int(row.total_duration_seconds),
            "total_energy_consumed_kwh": float(row.total_energy),
        }

    return stats_dict


async def get_current_charging_vehicles(db: AsyncSession):
    """获取当前正在充电和排队的车辆信息"""
    result = await db.execute(
        select(models.ChargingRequest, models.User.username, models.ChargingPile.pile_code)
        .join(models.User, models.ChargingRequest.user_id == models.User.user_id)
        .outerjoin(models.ChargingPile, models.ChargingRequest.assigned_pile_id == models.ChargingPile.pile_id)
        .filter(models.ChargingRequest.status.in_([models.RequestStatus.WAITING, models.RequestStatus.CHARGING]))
        .order_by(models.ChargingRequest.request_time)
    )

    vehicles = []
    for request, username, pile_code in result:
        vehicles.append(
            {
                "request_id": request.request_id,
                "user_id": request.user_id,
                "username": username,
                "queue_number": request.queue_number,
                "requested_charge_amount": float(request.requested_charge_amount),
                "status": request.status.value,
                "request_time": request.request_time,
                "assigned_pile_id": request.assigned_pile_id,
                "pile_code": pile_code,
                "start_time": request.start_time,
            }
        )

    return vehicles


async def update_pile_status(db: AsyncSession, pile_id: int, new_status: models.PileStatus, details: str):
    pile = await db.get(models.ChargingPile, pile_id)
    if not pile:
        raise ValueError("Pile not found")

    pile.status = new_status
    pile.status_details = details
    await db.commit()
    await db.refresh(pile)
    return pile


async def get_charging_request_by_pile_id(db: AsyncSession, pile_id: int) -> Optional[models.ChargingRequest]:
    """
    Gets the request that is currently in 'CHARGING' state on a specific pile.
    """
    result = await db.execute(
        select(models.ChargingRequest)
        .where(models.ChargingRequest.assigned_pile_id == pile_id)
        .where(models.ChargingRequest.status == models.RequestStatus.CHARGING)
    )
    return result.scalars().first()
