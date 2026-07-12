from flask import Blueprint, request, jsonify
from app.database import SessionLocal
from app.models import FuelLog, Expense, Vehicle, ExpenseCategory
from decimal import Decimal
from datetime import datetime
from app.utils import parse_date

operations_bp = Blueprint('operations', __name__)

@operations_bp.route('/fuel-logs', methods=['GET'])
def list_fuel():
    session = SessionLocal()
    logs = session.query(FuelLog).all()
    
    result = []
    for l in logs:
        vehicle = session.query(Vehicle).filter_by(id=l.vehicle_id).first()
        result.append({
            "id": l.id,
            "vehicle_id": vehicle.plate_number if vehicle else None,
            "liters": float(l.liters),
            "amount": float(l.cost),
            "date": str(l.date),
            "type": "Fuel"
        })
    return jsonify(result), 200

@operations_bp.route('/fuel-logs', methods=['POST'])
def add_fuel():
    data = request.get_json() or {}
    plate_number = data.get('vehicle_id')
    liters = data.get('liters')
    amount = data.get('amount')
    date_str = data.get('date')

    if not plate_number or liters is None or amount is None or not date_str:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Required fields missing"}}), 400

    session = SessionLocal()
    vehicle = session.query(Vehicle).filter_by(plate_number=plate_number).first()
    if not vehicle:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Vehicle not found"}}), 404

    log = FuelLog(
        vehicle_id=vehicle.id,
        liters=Decimal(str(liters)),
        cost=Decimal(str(amount)),
        date=parse_date(date_str) or datetime.utcnow().date(),
        odometer_reading=vehicle.current_odometer
    )
    session.add(log)
    session.commit()

    return jsonify({
        "id": log.id,
        "vehicle_id": vehicle.plate_number,
        "liters": float(log.liters),
        "amount": float(log.cost),
        "date": str(log.date),
        "type": "Fuel"
    }), 201
