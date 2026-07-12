from flask import Blueprint, request, jsonify
from app.database import SessionLocal
from app.models import Vehicle, VehicleStatus
from decimal import Decimal

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('', methods=['GET'])
def list_vehicles():
    session = SessionLocal()
    vehicles = session.query(Vehicle).all()
    
    result = []
    for v in vehicles:
        result.append({
            "id": v.id,
            "registration_number": v.plate_number,
            "vehicle_name": v.model,
            "type": v.type,
            "max_load_capacity": float(v.max_load_capacity),
            "odometer": float(v.current_odometer),
            "acquisition_cost": float(v.acquisition_cost),
            "status": v.status.value
        })
    return jsonify(result), 200

@vehicles_bp.route('', methods=['POST'])
def add_vehicle():
    data = request.get_json() or {}
    plate_number = data.get('registration_number')
    model = data.get('vehicle_name')
    v_type = data.get('type')
    max_load = data.get('max_load_capacity')
    odometer = data.get('odometer', 0)
    cost = data.get('acquisition_cost', 0)

    if not plate_number or not model or not v_type or max_load is None:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Required parameters missing"}}), 400

    session = SessionLocal()
    existing = session.query(Vehicle).filter_by(plate_number=plate_number).first()
    if existing:
        return jsonify({"error": {"code": "CONFLICT", "message": "Vehicle plate number already exists"}}), 409

    vehicle = Vehicle(
        plate_number=plate_number,
        model=model,
        type=v_type,
        region="Default Region",
        max_load_capacity=Decimal(str(max_load)),
        current_odometer=Decimal(str(odometer)),
        acquisition_cost=Decimal(str(cost)),
        status=VehicleStatus.available
    )
    session.add(vehicle)
    session.commit()

    return jsonify({
        "id": vehicle.id,
        "registration_number": vehicle.plate_number,
        "vehicle_name": vehicle.model,
        "type": vehicle.type,
        "max_load_capacity": float(vehicle.max_load_capacity),
        "odometer": float(vehicle.current_odometer),
        "acquisition_cost": float(vehicle.acquisition_cost),
        "status": vehicle.status.value
    }), 201
