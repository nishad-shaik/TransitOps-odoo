from flask import Blueprint, request, jsonify
from app.database import SessionLocal
from app.models import Maintenance, MaintenanceStatus, Vehicle, VehicleStatus
from app.utils import parse_date
from decimal import Decimal
from datetime import datetime

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('', methods=['GET'])
def list_logs():
    session = SessionLocal()
    logs = session.query(Maintenance).all()
    
    result = []
    for m in logs:
        vehicle = session.query(Vehicle).filter_by(id=m.vehicle_id).first()
        result.append({
            "id": m.id,
            "vehicle_id": vehicle.plate_number if vehicle else None,
            "description": m.description,
            "cost": float(m.cost),
            "date": str(m.start_date),
            "status": m.status.value
        })
    return jsonify(result), 200

@maintenance_bp.route('', methods=['POST'])
def log_service():
    data = request.get_json() or {}
    plate_number = data.get('vehicle_id')
    desc = data.get('description')
    cost = data.get('cost', 0)
    date_str = data.get('date')

    if not plate_number or not desc or date_str is None:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Required fields missing"}}), 400

    session = SessionLocal()
    vehicle = session.query(Vehicle).filter_by(plate_number=plate_number).first()
    if not vehicle:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Vehicle registry entry not found"}}), 404

    # Save active Maintenance log
    m = Maintenance(
        vehicle_id=vehicle.id,
        description=desc,
        cost=Decimal(str(cost)),
        start_date=parse_date(date_str) or datetime.utcnow().date(),
        status=MaintenanceStatus.open
    )
    
    # Cascade status update: Available -> In Shop
    if vehicle.status == VehicleStatus.available:
        vehicle.status = VehicleStatus.maintenance

    session.add(m)
    session.commit()

    return jsonify({
        "id": m.id,
        "vehicle_id": vehicle.plate_number,
        "description": m.description,
        "cost": float(m.cost),
        "date": str(m.start_date),
        "status": m.status.value
    }), 201
