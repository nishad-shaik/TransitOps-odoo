from flask import Blueprint, request, jsonify
from app.database import SessionLocal
from app.models import Maintenance, MaintenanceStatus, Vehicle, VehicleStatus
from app.decorators import token_required, roles_accepted
from app.utils import parse_date
from decimal import Decimal
from datetime import datetime

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('', methods=['GET'])
@token_required
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
@roles_accepted('Admin', 'Mechanic')
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

@maintenance_bp.route('/<int:log_id>', methods=['PATCH'])
@token_required
def close_maintenance_log(log_id):
    data = request.get_json() or {}
    new_status = data.get('status')
    
    if not new_status or new_status != 'Closed':
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Only status 'Closed' is acceptable for this action"}}), 400
        
    session = SessionLocal()
    log = session.query(Maintenance).filter_by(id=log_id).first()
    if not log:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Maintenance log not found"}}), 404
        
    log.status = MaintenanceStatus.closed
    log.end_date = datetime.utcnow().date()
    
    vehicle = session.query(Vehicle).filter_by(id=log.vehicle_id).first()
    if vehicle and vehicle.status == VehicleStatus.maintenance:
        vehicle.status = VehicleStatus.available
        
    session.commit()
    
    return jsonify({
        "id": log.id,
        "status": log.status.value,
        "vehicle_id": vehicle.plate_number if vehicle else None
    }), 200

