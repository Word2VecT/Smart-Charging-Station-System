from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from .models import PileStatus, PileType, ReportType, RequestStatus, RequestType, UserRole


# Base Schemas
class UserBase(BaseModel):
    username: str
    role: UserRole = UserRole.USER


class ChargingPileBase(BaseModel):
    pile_code: str
    type: PileType
    status: PileStatus
    power_rate: Decimal


class ChargingRequestBase(BaseModel):
    user_id: int
    requested_charge_type: RequestType
    requested_charge_amount: Decimal


class ChargingOrderBase(BaseModel):
    request_id: int
    user_id: int
    pile_id: int
    start_time: datetime
    end_time: datetime
    actual_charge_amount: Decimal
    charge_fee: Decimal
    service_fee: Decimal
    total_fee: Decimal


class OperationalReportBase(BaseModel):
    report_type: ReportType
    report_date: date
    pile_id: Optional[int] = None
    total_charges: int
    total_charging_duration_seconds: int
    total_energy_consumed_kwh: Decimal
    total_charge_fee: Decimal
    total_service_fee: Decimal
    total_revenue: Decimal


# Create Schemas
class UserCreate(UserBase):
    password: str


class ChargingPileCreate(ChargingPileBase):
    pass


class ChargingRequestBody(BaseModel):
    """Schema for the body of a new request, without user_id."""

    requested_charge_type: RequestType
    requested_charge_amount: Decimal


class ChargingRequestCreate(ChargingRequestBase):
    pass


class ChargingOrderCreate(ChargingOrderBase):
    pass


class SchedulingStrategy(BaseModel):
    strategy: str

    class Config:
        orm_mode = True


class SchedulingStrategyUpdate(BaseModel):
    strategy: str


class OperationalReportCreate(OperationalReportBase):
    pass


# Update Schemas
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class ChargingPileUpdate(BaseModel):
    status: Optional[PileStatus] = None


class ChargingRequestUpdate(BaseModel):
    requested_charge_type: Optional[RequestType] = None
    requested_charge_amount: Optional[Decimal] = None
    status: Optional[RequestStatus] = None


# Read Schemas (for API responses)
class User(UserBase):
    user_id: int
    registration_date: datetime

    class Config:
        from_attributes = True


class ChargingPile(ChargingPileBase):
    pile_id: int

    class Config:
        from_attributes = True


class ChargingRequest(ChargingRequestBase):
    request_id: int
    queue_number: Optional[str] = None
    status: RequestStatus
    request_time: datetime
    assigned_pile_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChargingOrder(ChargingOrderBase):
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OperationalReport(OperationalReportBase):
    report_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Token Schema for authentication
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Admin Schemas


class AdminBase(BaseModel):
    username: str


class AdminCreate(BaseModel):
    username: str
    password: str


class Admin(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


# PileLog Schemas
class PileLogBase(BaseModel):
    pile_id: int
    event_type: str
    details: Optional[str] = None


class PileLogCreate(PileLogBase):
    pass


class PileLog(PileLogBase):
    log_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# History Schema
class HistoryItem(BaseModel):
    """
    A unified schema for displaying both charging requests and completed orders in a history view.
    """

    item_id: int  # Either request_id or order_id
    item_type: str  # "REQUEST" or "ORDER"
    status: str  # Combined status from RequestStatus or a simple "COMPLETED" for orders
    date: datetime  # request_time for requests, created_at for orders
    requested_charge_amount: Optional[Decimal] = None
    actual_charge_amount: Optional[Decimal] = None
    total_fee: Optional[Decimal] = None
    charge_type: Optional[RequestType] = None


# ===================
# 管理员仪表盘相关 Schema
# ===================


class PileStatistics(BaseModel):
    pile_id: int
    total_charges: int
    total_charging_duration_seconds: int
    total_energy_consumed_kwh: float


class CurrentVehicle(BaseModel):
    request_id: int
    user_id: int
    username: str
    queue_number: Optional[str]
    requested_charge_amount: float
    status: str
    request_time: datetime
    assigned_pile_id: Optional[int]
    pile_code: Optional[str]
    start_time: Optional[datetime]


class PileWithStatistics(BaseModel):
    pile_id: int
    pile_code: str
    type: PileType
    status: PileStatus
    power_rate: Decimal
    statistics: PileStatistics


class DashboardData(BaseModel):
    piles: List[PileWithStatistics]
    current_vehicles: List[CurrentVehicle]


class PileSetup(BaseModel):
    fast_piles: int
    trickle_piles: int


class OrderDetail(BaseModel):
    """
    Schema for the detailed view of a charging order.
    """

    order_id: int
    created_at: datetime
    pile_code: str
    actual_charge_amount: Decimal
    charge_duration_seconds: int
    start_time: datetime
    end_time: datetime
    charge_fee: Decimal
    service_fee: Decimal
    total_fee: Decimal

    class Config:
        from_attributes = True
