import enum

from sqlalchemy import BigInteger, Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class PileType(str, enum.Enum):
    FAST = "FAST"
    TRICKLE = "TRICKLE"


class PileStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    CHARGING = "CHARGING"
    FAULTY = "FAULTY"
    OFF = "OFF"


class RequestType(str, enum.Enum):
    FAST = "FAST"
    TRICKLE = "TRICKLE"


class RequestStatus(str, enum.Enum):
    WAITING = "WAITING"
    CHARGING = "CHARGING"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"


class ReportType(str, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(Enum(UserRole, native_enum=False), nullable=False, default=UserRole.USER)

    requests = relationship("ChargingRequest", back_populates="user")
    orders = relationship("ChargingOrder", back_populates="user")


class ChargingPile(Base):
    __tablename__ = "chargingpiles"
    pile_id = Column(Integer, primary_key=True, index=True)
    pile_code = Column(String(10), unique=True, nullable=False)
    type = Column(Enum(PileType, native_enum=False), nullable=False)
    status = Column(Enum(PileStatus, native_enum=False), nullable=False, default=PileStatus.OFF)
    power_rate = Column(Numeric(10, 2), nullable=False)

    requests = relationship("ChargingRequest", back_populates="pile")
    orders = relationship("ChargingOrder", back_populates="pile")
    reports = relationship("OperationalReport", back_populates="pile")


class ChargingRequest(Base):
    __tablename__ = "chargingrequests"
    request_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    queue_number = Column(String(20), unique=True)
    requested_charge_type = Column(Enum(RequestType, native_enum=False), nullable=False)
    requested_charge_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(RequestStatus, native_enum=False), nullable=False, default=RequestStatus.WAITING, index=True)
    request_time = Column(DateTime(timezone=True), server_default=func.now())
    assigned_pile_id = Column(Integer, ForeignKey("chargingpiles.pile_id"))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="requests")
    pile = relationship("ChargingPile", back_populates="requests")
    order = relationship("ChargingOrder", back_populates="request", uselist=False)


class ChargingOrder(Base):
    __tablename__ = "chargingorders"
    order_id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("chargingrequests.request_id"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    pile_id = Column(Integer, ForeignKey("chargingpiles.pile_id"), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    actual_charge_amount = Column(Numeric(10, 2), nullable=False)
    charge_fee = Column(Numeric(10, 2), nullable=False)
    service_fee = Column(Numeric(10, 2), nullable=False)
    total_fee = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    request = relationship("ChargingRequest", back_populates="order")
    user = relationship("User", back_populates="orders")
    pile = relationship("ChargingPile", back_populates="orders")


class OperationalReport(Base):
    __tablename__ = "operationalreports"
    report_id = Column(Integer, primary_key=True, index=True)
    report_type = Column(Enum(ReportType, native_enum=False), nullable=False)
    report_date = Column(Date, nullable=False, index=True)
    pile_id = Column(Integer, ForeignKey("chargingpiles.pile_id"))
    total_charges = Column(Integer, nullable=False)
    total_charging_duration_seconds = Column(BigInteger, nullable=False)
    total_energy_consumed_kwh = Column(Numeric(15, 2), nullable=False)
    total_charge_fee = Column(Numeric(15, 2), nullable=False)
    total_service_fee = Column(Numeric(15, 2), nullable=False)
    total_revenue = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    pile = relationship("ChargingPile", back_populates="reports")


class PileLog(Base):
    __tablename__ = "pilelogs"
    log_id = Column(Integer, primary_key=True, index=True)
    pile_id = Column(Integer, ForeignKey("chargingpiles.pile_id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(String(50), nullable=False)  # e.g., 'STATUS_CHANGE', 'DATA_REPORT'
    details = Column(String(255))

    pile = relationship("ChargingPile")


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
