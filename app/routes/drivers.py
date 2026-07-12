from flask import Blueprint, request, jsonify
from app.database import SessionLocal
from app.models import Driver, DriverStatus
from app.decorators import token_required, roles_accepted
from app.utils import parse_date
from decimal import Decimal

drivers_bp = Blueprint('drivers', __name__)

@drivers_bp.route('', methods=['GET'])
@token_required
def list_drivers():
    session = SessionLocal()
    drivers = session.query(Driver).all()
    
    result = []
    for d in drivers:
        result.append({
            "id": d.id,
            "name": d.name,
            "license_number": d.license_number,
            "license_category": d.license_category,
            "license_expiry_date": str(d.license_expiry_date),
            "contact_number": d.contact_number,
            "safety_score": float(d.safety_score),
            "status": d.status.value,
            "tripCompletionRate": 100 # Mock placeholder rate
        })
    return jsonify(result), 200

@drivers_bp.route('', methods=['POST'])
@roles_accepted('Admin')
def add_driver():
    data = request.get_json() or {}
    name = data.get('name')
    license_num = data.get('license_number')
    category = data.get('license_category')
    expiry_str = data.get('license_expiry_date')
    contact = data.get('contact_number')
    score = data.get('safety_score', 100)

    if not name or not license_num or not category or not expiry_str or not contact:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Required fields missing"}}), 400

    expiry_date = parse_date(expiry_str)
    if not expiry_date:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Invalid date format for license_expiry_date"}}), 400

    session = SessionLocal()
    existing = session.query(Driver).filter_by(license_number=license_num).first()
    if existing:
        return jsonify({"error": {"code": "CONFLICT", "message": "Driver license number already exists"}}), 409

    driver = Driver(
        name=name,
        license_number=license_num,
        license_category=category,
        license_expiry_date=expiry_date,
        contact_number=contact,
        safety_score=Decimal(str(score)),
        status=DriverStatus.available
    )
    session.add(driver)
    session.commit()

    return jsonify({
        "id": driver.id,
        "name": driver.name,
        "license_number": driver.license_number,
        "license_category": driver.license_category,
        "license_expiry_date": str(driver.license_expiry_date),
        "contact_number": driver.contact_number,
        "safety_score": float(driver.safety_score),
        "status": driver.status.value,
        "tripCompletionRate": 100
    }), 201
