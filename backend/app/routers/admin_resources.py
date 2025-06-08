from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import crud, models, schemas
from ..auth import get_current_admin_user
from ..database import get_db

router = APIRouter(prefix="/admin", tags=["Admin Access"])

# ✅ 查看所有用户
@router.get("/users", response_model=List[schemas.User])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin_user)
):
    return await crud.get_users(db)

# ✅ 查看所有订单
@router.get("/orders", response_model=List[schemas.ChargingOrder])
async def get_all_orders(
    db: AsyncSession = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin_user)
):
    orders = await crud.get_all_orders(db)
    for order in orders:
        await db.refresh(order, attribute_names=["request"])
    return orders

# ✅ 查看所有请求
@router.get("/requests", response_model=List[schemas.ChargingRequest])
async def get_all_requests(
    db: AsyncSession = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin_user)
):
    return await crud.get_requests(db)
