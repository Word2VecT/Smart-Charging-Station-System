from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from .. import crud, schemas, models
from ..database import get_db
from ..auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_admin_user

router = APIRouter(prefix="/admin-auth", tags=["Admin Authentication"])

# ❌ 注释掉注册接口，避免用户自行注册管理员账号
# @router.post("/register", response_model=schemas.Admin)
# async def register_admin(admin: schemas.AdminCreate, db: AsyncSession = Depends(get_db)):
#     db_admin = await crud.get_admin_by_username(db, admin.username)
#     if db_admin:
#         raise HTTPException(status_code=400, detail="Admin already exists")
#     return await crud.create_admin(db, admin)

# ✅ 管理员登录接口
@router.post("/token", response_model=schemas.Token)
async def login_admin_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    admin = await crud.authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username, "role": "admin"},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ 获取当前管理员信息接口（用于 useAdminAuth 的 fetchAdmin）
@router.get("/me", response_model=schemas.Admin)
async def get_current_admin(admin: models.Admin = Depends(get_current_admin_user)):
    return admin
