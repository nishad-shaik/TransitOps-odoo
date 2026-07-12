import argparse
import os
import random
import sys
import uuid
import hashlib  # Changed to native hashlib to bypass the broken passlib/bcrypt combination
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import (
    Base,
    Driver,
    DriverStatus,
    Expense,
    ExpenseCategory,
    FuelLog,
    Maintenance,
    MaintenanceStatus,
    Trip,
    TripStatus,
    User,
    UserRole,
    Vehicle,
    VehicleStatus,
)

DEFAULT_DB_URL = "sqlite:///transitops.db"


def hash_password(password: str) -> str:
    """Safe native fallback for seeding passwords without depending on broken passlib mixins."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_engine():
    db_url = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)
    return create_engine(db_url, echo=False, future=True, pool_pre_ping=True, pool_recycle=280)


def init_schema(engine, drop_first: bool = False):
    if drop_first:
        print("Dropping all tables...")
        Base.metadata.drop_all(engine)
    print("Creating all tables...")
    Base.metadata.create_all(engine)
    print("Schema ready.")


VEHICLE_MODELS = {
    "Van": ["Ford Transit", "Mercedes Sprinter", "Renault Trafic"],
    "Truck": ["Isuzu NPR", "Volvo FH", "Tata LPT 1613"],
    "Refrigerated Truck": ["Isuzu Reefer", "Hino 300 Reefer"],
    "Pickup": ["Toyota Hilux", "Ford Ranger"],
    "Bike": ["Bajaj CT100", "Honda CD70"],
}
CAPACITY_RANGE = {
    "Van": (400, 900),
    "Truck": (1500, 3000),
    "Refrigerated Truck": (1200, 2500),
    "Pickup": (500, 1200),
    "Bike": (20, 60),
}
COST_RANGE = {
    "Van": (22000, 35000),
    "Truck": (45000, 75000),
    "Refrigerated Truck": (55000, 85000),
    "Pickup": (18000, 28000),
    "Bike": (1500, 3000),
}
REGIONS = ["North", "South", "East", "West", "Central"]
CITIES = ["Warehouse A", "Depot 12", "Port Terminal", "Central Hub", "Retail Store 4",
          "Cold Storage 2", "Depot 7", "Distribution Center", "Client Site B", "Regional Yard"]
FIRST_NAMES = ["Alex", "Sam", "Jordan", "Taylor", "Priya", "Wei", "Fatima", "Diego",
               "Nia", "Ravi", "Elena", "Marcus", "Yuki", "Aisha", "Liam", "Sofia"]
LAST_NAMES = ["Morgan", "Rivera", "Blake", "Chen", "Sharma", "Zhang", "Hassan", "Diaz",
              "Okafor", "Patel", "Novak", "Reid", "Tanaka", "Bello", "Murphy", "Costa"]
LICENSE_CATEGORIES = ["Category B", "Category C", "Category D", "CDL-A", "CDL-B"]
MAINTENANCE_DESCRIPTIONS = ["Oil change", "Brake pad replacement", "Tire rotation",
                             "Engine diagnostics", "Transmission service", "AC repair",
                             "Battery replacement", "Suspension check", "Scheduled service"]


def seed_data(engine):
    random.seed(2026)  # deterministic output — same demo data every run

    with Session(engine) as session:
        if session.query(User).count() > 0:
            print("Data already present — skipping seed.")
            return

        print("Seeding sample data...")
        now = datetime.now(timezone.utc)

        # Users
        users = [
            User(email="admin@transitops.dev", password_hash=hash_password("password123"), role=UserRole.admin),
            User(email="dispatcher@transitops.dev", password_hash=hash_password("password123"), role=UserRole.dispatcher),
            User(email="mechanic@transitops.dev", password_hash=hash_password("password123"), role=UserRole.mechanic),
        ]
        driver_logins = [
            User(email=f"driver{i}@transitops.dev", password_hash=hash_password("password123"), role=UserRole.driver)
            for i in range(1, 6)
        ]
        session.add_all(users + driver_logins)
        session.flush()

        #  Vehicles 
        status_plan = (
            [VehicleStatus.available] * 10
            + [VehicleStatus.on_trip] * 3
            + [VehicleStatus.maintenance] * 3
            + [VehicleStatus.retired] * 2
        )
        random.shuffle(status_plan)

        vehicles = []
        counters = {}
        for status in status_plan:
            vtype = random.choice(list(VEHICLE_MODELS.keys()))
            counters[vtype] = counters.get(vtype, 0) + 1
            prefix = {"Van": "VAN", "Truck": "TRK", "Refrigerated Truck": "REF",
                      "Pickup": "PIK", "Bike": "BIK"}[vtype]
            lo, hi = CAPACITY_RANGE[vtype]
            clo, chi = COST_RANGE[vtype]
            vehicles.append(Vehicle(
                plate_number=f"{prefix}-{counters[vtype]:02d}",
                model=random.choice(VEHICLE_MODELS[vtype]),
                type=vtype,
                region=random.choice(REGIONS),
                status=status,
                max_load_capacity=random.randint(lo, hi),
                current_odometer=random.randint(2000, 90000),
                acquisition_cost=random.randint(clo, chi),
            ))
        session.add_all(vehicles)
        session.flush()

        vehicles_by_status = {s: [v for v in vehicles if v.status == s] for s in VehicleStatus}

        # Drivers
        driver_status_plan = (
            [DriverStatus.available] * 9
            + [DriverStatus.on_trip] * 3
            + [DriverStatus.off_duty] * 2
            + [DriverStatus.suspended] * 2
        )
        random.shuffle(driver_status_plan)

        used_names = set()
        drivers = []
        for idx, status in enumerate(driver_status_plan):
            while True:
                name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
                if name not in used_names:
                    used_names.add(name)
                    break
            is_expired_case = (status == DriverStatus.available and idx == 0)
            expiry = (
                date.today() - timedelta(days=30)
                if is_expired_case
                else date.today() + timedelta(days=random.randint(30, 720))
            )
            drivers.append(Driver(
                user_id=driver_logins[idx].id if idx < len(driver_logins) else None,
                name=name,
                license_number=f"DL-{random.randint(10000, 99999)}",
                license_category=random.choice(LICENSE_CATEGORIES),
                license_expiry_date=expiry,
                contact_number=f"+1-555-{random.randint(1000, 9999)}",
                safety_score=random.randint(55, 100),
                status=status,
            ))
        session.add_all(drivers)
        session.flush()

        drivers_by_status = {s: [d for d in drivers if d.status == s] for s in DriverStatus}

        # Maintenance 
        maintenance_records = []
        for v in vehicles_by_status[VehicleStatus.maintenance]:
            maintenance_records.append(Maintenance(
                vehicle_id=v.id,
                description=random.choice(MAINTENANCE_DESCRIPTIONS),
                cost=round(random.uniform(80, 600), 2),
                status=MaintenanceStatus.open,
                start_date=date.today() - timedelta(days=random.randint(0, 5)),
                end_date=None,
            ))
        for v in random.sample(vehicles, 8):
            start = date.today() - timedelta(days=random.randint(20, 300))
            maintenance_records.append(Maintenance(
                vehicle_id=v.id,
                description=random.choice(MAINTENANCE_DESCRIPTIONS),
                cost=round(random.uniform(60, 800), 2),
                status=MaintenanceStatus.closed,
                start_date=start,
                end_date=start + timedelta(days=random.randint(1, 3)),
            ))
        session.add_all(maintenance_records)

        # Trips
        trips = []

        def cargo_for(vehicle):
            return round(float(vehicle.max_load_capacity) * random.uniform(0.2, 0.9), 2)

        on_trip_drivers = drivers_by_status[DriverStatus.on_trip][:]
        random.shuffle(on_trip_drivers)
        for v, d in zip(vehicles_by_status[VehicleStatus.on_trip], on_trip_drivers):
            trips.append(Trip(
                vehicle_id=v.id, driver_id=d.id,
                origin=random.choice(CITIES), destination=random.choice(CITIES),
                cargo_weight=cargo_for(v), planned_distance=random.randint(30, 400),
                status=TripStatus.ongoing,
                start_time=now - timedelta(hours=random.randint(1, 6)),
            ))

        avail_vehicles = vehicles_by_status[VehicleStatus.available][:]
        avail_drivers = drivers_by_status[DriverStatus.available][:]
        random.shuffle(avail_vehicles)
        random.shuffle(avail_drivers)
        n_scheduled = min(6, len(avail_vehicles), len(avail_drivers))
        for v, d in zip(avail_vehicles[:n_scheduled], avail_drivers[:n_scheduled]):
            trips.append(Trip(
                vehicle_id=v.id, driver_id=d.id,
                origin=random.choice(CITIES), destination=random.choice(CITIES),
                cargo_weight=cargo_for(v), planned_distance=random.randint(20, 350),
                status=TripStatus.scheduled,
                start_time=now + timedelta(hours=random.randint(2, 72)),
            ))

        for _ in range(30):
            v = random.choice(vehicles)
            d = random.choice(drivers)
            start = now - timedelta(days=random.randint(1, 90), hours=random.randint(0, 23))
            duration = timedelta(hours=random.randint(2, 30))
            trips.append(Trip(
                vehicle_id=v.id, driver_id=d.id,
                origin=random.choice(CITIES), destination=random.choice(CITIES),
                cargo_weight=cargo_for(v),
                planned_distance=random.randint(20, 400),
                actual_distance=random.randint(20, 420),
                status=TripStatus.completed,
                start_time=start, end_time=start + duration,
            ))

        for _ in range(5):
            v = random.choice(vehicles)
            d = random.choice(drivers)
            start = now - timedelta(days=random.randint(1, 60))
            trips.append(Trip(
                vehicle_id=v.id, driver_id=d.id,
                origin=random.choice(CITIES), destination=random.choice(CITIES),
                cargo_weight=cargo_for(v), planned_distance=random.randint(20, 300),
                status=TripStatus.cancelled, start_time=start,
            ))

        session.add_all(trips)
        session.flush()

        # Fuel logs
        fuel_logs = []
        completed_trips = [t for t in trips if t.status == TripStatus.completed]
        for t in random.sample(completed_trips, k=min(20, len(completed_trips))):
            liters = round(random.uniform(15, 120), 2)
            fuel_logs.append(FuelLog(
                vehicle_id=t.vehicle_id, trip_id=t.id,
                liters=liters, cost=round(liters * random.uniform(0.9, 1.6), 2),
                odometer_at_fuel=random.randint(2000, 90000),
                logged_at=t.end_time or t.start_time,
            ))
        
        for v in random.sample(vehicles, 10):
            liters = round(random.uniform(10, 100), 2)
            fuel_logs.append(FuelLog(
                vehicle_id=v.id, trip_id=None,
                liters=liters, cost=round(liters * random.uniform(0.9, 1.6), 2),
                odometer_at_fuel=random.randint(2000, 90000),
                logged_at=now - timedelta(days=random.randint(1, 60)),
            ))
        session.add_all(fuel_logs)

        # Expenses 
        expenses = []
        for t in random.sample(completed_trips, k=min(15, len(completed_trips))):
            expenses.append(Expense(
                vehicle_id=t.vehicle_id, trip_id=t.id,
                category=ExpenseCategory.toll, amount=round(random.uniform(3, 40), 2),
                logged_at=t.end_time or t.start_time,
            ))
        for v in vehicles:
            expenses.append(Expense(
                vehicle_id=v.id, trip_id=None,
                category=ExpenseCategory.insurance, amount=round(random.uniform(200, 900), 2),
                logged_at=now - timedelta(days=random.randint(30, 300)),
            ))
            if random.random() < 0.4:
                expenses.append(Expense(
                    vehicle_id=v.id, trip_id=None,
                    category=random.choice([ExpenseCategory.permits, ExpenseCategory.other]),
                    amount=round(random.uniform(20, 250), 2),
                    logged_at=now - timedelta(days=random.randint(1, 200)),
                ))
        session.add_all(expenses)

        session.commit()
        print(
            f"Seed data inserted: {len(users) + len(driver_logins)} users, "
            f"{len(vehicles)} vehicles, {len(drivers)} drivers, {len(trips)} trips, "
            f"{len(maintenance_records)} maintenance records, {len(fuel_logs)} fuel logs, "
            f"{len(expenses)} expenses."
        )


def main():
    parser = argparse.ArgumentParser(description="Initialize the TransitOps database.")
    parser.add_argument("--seed", action="store_true", help="Insert sample data after creating tables")
    parser.add_argument("--drop", action="store_true", help="Drop all tables before creating (dev only)")
    args = parser.parse_args()

    engine = get_engine()

    try:
        init_schema(engine, drop_first=args.drop)
        if args.seed:
            seed_data(engine)
    except Exception as exc:
        print(f"Database initialization failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()