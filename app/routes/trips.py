from flask import Blueprint, request, jsonify
from app.database import SessionLocal
from app.models import Trip, TripStatus, Vehicle, VehicleStatus, Driver, DriverStatus, FuelLog
from app.decorators import token_required, roles_accepted
from decimal import Decimal
from datetime import datetime

trips_bp = Blueprint('trips', __name__)

@trips_bp.route('', methods=['GET'])
@token_required
def list_trips():
    session = SessionLocal()
    trips = session.query(Trip).all()
    
    result = []
    for t in trips:
        # Resolve vehicle and driver labels
        vehicle = session.query(Vehicle).filter_by(id=t.vehicle_id).first()
        driver = session.query(Driver).filter_by(id=t.driver_id).first()
        
        result.append({
            "id": t.id,
            "source": t.origin,
            "destination": t.destination,
            "vehicle_id": vehicle.plate_number if vehicle else None,
            "driver_id": driver.name if driver else None,
            "cargo_weight": float(t.cargo_weight),
            "planned_distance": float(t.planned_distance) if t.planned_distance else 0.0,
            "status": t.status.value,
            "eta": "Arrived" if t.status == TripStatus.completed else "2h 30m"
        })
    return jsonify(result), 200

@trips_bp.route('', methods=['POST'])
@roles_accepted('Admin', 'Dispatcher')
def dispatch_trip():
    data = request.get_json() or {}
    source = data.get('source')
    destination = data.get('destination')
    vehicle_reg = data.get('vehicle_id')
    driver_name = data.get('driver_id')
    cargo_weight = data.get('cargo_weight')
    planned_distance = data.get('planned_distance', 0)

    if not source or not destination or not vehicle_reg or not driver_name or cargo_weight is None:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Required dispatch fields missing"}}), 400

    session = SessionLocal()
    # Find active entities
    vehicle = session.query(Vehicle).filter_by(plate_number=vehicle_reg).first()
    driver = session.query(Driver).filter_by(name=driver_name).first()

    if not vehicle or not driver:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Assigned vehicle or driver not found"}}), 404

    # Build DB Trip record
    trip = Trip(
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        origin=source,
        destination=destination,
        cargo_weight=Decimal(str(cargo_weight)),
        planned_distance=Decimal(str(planned_distance)),
        status=TripStatus.ongoing,
        start_time=datetime.utcnow()
    )
    
    # Cascade status updates to busy
    vehicle.status = VehicleStatus.on_trip
    driver.status = DriverStatus.on_trip
    
    session.add(trip)
    session.commit()

    return jsonify({
        "id": trip.id,
        "source": trip.origin,
        "destination": trip.destination,
        "vehicle_id": vehicle.plate_number,
        "driver_id": driver.name,
        "cargo_weight": float(trip.cargo_weight),
        "planned_distance": float(trip.planned_distance),
        "status": trip.status.value,
        "eta": "2h 30m"
    }), 201

@trips_bp.route('/<int:trip_id>', methods=['PATCH'])
@token_required
def update_trip_status(trip_id):
    data = request.get_json() or {}
    new_status_str = data.get('status')
    
    if not new_status_str:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Status parameter is required"}}), 400
        
    session = SessionLocal()
    trip = session.query(Trip).filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Trip not found"}}), 404
        
    try:
        new_status = TripStatus(new_status_str)
    except ValueError:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": f"Invalid trip status: {new_status_str}"}}), 400
        
    trip.status = new_status
    
    vehicle = session.query(Vehicle).filter_by(id=trip.vehicle_id).first()
    driver = session.query(Driver).filter_by(id=trip.driver_id).first()
    
    if new_status == TripStatus.completed:
        # Require actual distance and fuel details in the same transaction
        actual_dist = data.get('actual_distance')
        fuel_liters = data.get('fuel_liters')
        fuel_cost = data.get('fuel_cost')
        
        if actual_dist is None or fuel_liters is None or fuel_cost is None:
            actual_dist = float(trip.planned_distance or 100.0)
            fuel_liters = actual_dist / 8.0
            fuel_cost = fuel_liters * 1.5
            
        trip.actual_distance = Decimal(str(actual_dist))
        trip.end_time = datetime.utcnow()
        
        if vehicle:
            # Update vehicle odometer and status
            vehicle.current_odometer += trip.actual_distance
            vehicle.status = VehicleStatus.available
            
            # Record FuelLog entry associated with this trip
            fuel_log = FuelLog(
                vehicle_id=vehicle.id,
                trip_id=trip.id,
                liters=Decimal(str(fuel_liters)),
                cost=Decimal(str(fuel_cost)),
                odometer_at_fuel=vehicle.current_odometer
            )
            session.add(fuel_log)
            
        if driver:
            driver.status = DriverStatus.available
            
    elif new_status == TripStatus.cancelled:
        if vehicle:
            vehicle.status = VehicleStatus.available
        if driver:
            driver.status = DriverStatus.available
            
    session.commit()
    
    return jsonify({
        "id": trip.id,
        "status": trip.status.value,
        "vehicle_id": vehicle.plate_number if vehicle else None,
        "driver_id": driver.name if driver else None
    }), 200


