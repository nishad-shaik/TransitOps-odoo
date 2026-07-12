import enum
import uuid
from sqlalchemy import (
    CHAR,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    Boolean,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

def uuid_pk():
    return Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

def enum_col(py_enum, name, **kwargs):
    return Column(
        Enum(py_enum, name=name, values_callable=lambda e: [m.value for m in e]),
        **kwargs,
    )

# Enums
class UserRole(str, enum.Enum):
    admin = "Admin"
    dispatcher = "Dispatcher"
    driver = "Driver"
    mechanic = "Mechanic"
    safety_officer = "Safety Officer"
    financial_analyst = "Financial Analyst"

class VehicleStatus(str, enum.Enum):
    available = "Available"
    on_trip = "On Trip"
    maintenance = "Maintenance"
    retired = "Retired"

class DriverStatus(str, enum.Enum):
    available = "Available"
    on_trip = "On Trip"
    off_duty = "Off Duty"
    suspended = "Suspended"

class TripStatus(str, enum.Enum):
    scheduled = "Scheduled"
    ongoing = "Ongoing"
    completed = "Completed"
    cancelled = "Cancelled"

class MaintenanceStatus(str, enum.Enum):
    open = "Open"
    closed = "Closed"

class ExpenseCategory(str, enum.Enum):
    toll = "Toll"
    insurance = "Insurance"
    permits = "Permits"
    other = "Other"

# Tables
class User(Base):
    __tablename__ = "users"
    id = uuid_pk()
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = enum_col(UserRole, "user_role", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    driver = relationship("Driver", back_populates="user", uselist=False)

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = uuid_pk()
    plate_number = Column(String(255), unique=True, nullable=False)
    model = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    status = enum_col(VehicleStatus, "vehicle_status", nullable=False, default=VehicleStatus.available)
    max_load_capacity = Column(Numeric(10, 2), nullable=False)
    current_odometer = Column(Numeric(10, 2), nullable=False, default=0)
    acquisition_cost = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    trips = relationship("Trip", back_populates="vehicle")
    maintenance_records = relationship("Maintenance", back_populates="vehicle")
    fuel_logs = relationship("FuelLog", back_populates="vehicle")
    expenses = relationship("Expense", back_populates="vehicle")
    __table_args__ = (
        CheckConstraint("max_load_capacity > 0", name="ck_vehicle_max_load_positive"),
        CheckConstraint("acquisition_cost >= 0", name="ck_vehicle_acq_cost_nonneg"),
        CheckConstraint("current_odometer >= 0", name="ck_vehicle_odometer_nonneg"),
    )

class Driver(Base):
    __tablename__ = "drivers"
    id = uuid_pk()
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
    name = Column(String(255), nullable=False)
    license_number = Column(String(255), unique=True, nullable=False)
    license_category = Column(String(50), nullable=False)
    license_expiry_date = Column(Date, nullable=False)
    contact_number = Column(String(50), nullable=False)
    safety_score = Column(Numeric(5, 2), nullable=False, default=100)
    status = enum_col(DriverStatus, "driver_status", nullable=False, default=DriverStatus.available)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="driver")
    trips = relationship("Trip", back_populates="driver")
    __table_args__ = (
        CheckConstraint("safety_score >= 0 AND safety_score <= 100", name="ck_driver_safety_score_range"),
    )

class Trip(Base):
    __tablename__ = "trips"
    id = uuid_pk()
    vehicle_id = Column(CHAR(36), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False)
    driver_id = Column(CHAR(36), ForeignKey("drivers.id", ondelete="RESTRICT"), nullable=False)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    cargo_weight = Column(Numeric(10, 2), nullable=False)
    planned_distance = Column(Numeric(10, 2), nullable=True)
    actual_distance = Column(Numeric(10, 2), nullable=True)
    status = enum_col(TripStatus, "trip_status", nullable=False, default=TripStatus.scheduled)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    fuel_logs = relationship("FuelLog", back_populates="trip")
    expenses = relationship("Expense", back_populates="trip")
    __table_args__ = (
        CheckConstraint("cargo_weight >= 0", name="ck_trip_cargo_weight_nonneg"),
    )

class Maintenance(Base):
    __tablename__ = "maintenance"
    id = uuid_pk()
    vehicle_id = Column(CHAR(36), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False)
    description = Column(Text, nullable=False)
    cost = Column(Numeric(10, 2), nullable=False, default=0)
    status = enum_col(MaintenanceStatus, "maintenance_status", nullable=False, default=MaintenanceStatus.open)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    vehicle = relationship("Vehicle", back_populates="maintenance_records")
    __table_args__ = (
        CheckConstraint("cost >= 0", name="ck_maintenance_cost_nonneg"),
        CheckConstraint(
            "(status = 'Closed' AND end_date IS NOT NULL) OR (status = 'Open')",
            name="ck_maintenance_closed_has_end_date",
        ),
    )

class FuelLog(Base):
    __tablename__ = "fuel_logs"
    id = uuid_pk()
    vehicle_id = Column(CHAR(36), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False)
    trip_id = Column(CHAR(36), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    liters = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)
    odometer_at_fuel = Column(Numeric(10, 2), nullable=True)
    logged_at = Column(DateTime, server_default=func.now())
    vehicle = relationship("Vehicle", back_populates="fuel_logs")
    trip = relationship("Trip", back_populates="fuel_logs")
    __table_args__ = (
        CheckConstraint("liters > 0", name="ck_fuel_liters_positive"),
        CheckConstraint("cost >= 0", name="ck_fuel_cost_nonneg"),
    )

class Expense(Base):
    __tablename__ = "expenses"
    id = uuid_pk()
    vehicle_id = Column(CHAR(36), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False)
    trip_id = Column(CHAR(36), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    category = enum_col(ExpenseCategory, "expense_category", nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    logged_at = Column(DateTime, server_default=func.now())
    vehicle = relationship("Vehicle", back_populates="expenses")
    trip = relationship("Trip", back_populates="expenses")
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_expense_amount_nonneg"),
    )