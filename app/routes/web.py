from flask import Blueprint, jsonify
from app.database import SessionLocal
from app.models import Trip, TripStatus, Vehicle, VehicleStatus, Driver
from app.decorators import token_required

web_bp = Blueprint('web', __name__)

@web_bp.route('/status', methods=['GET'])
def server_status():
    return jsonify({"status": "healthy", "service": "TransitOps API Backend"}), 200

@web_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def dashboard_stats():
    session = SessionLocal()
    
    # 1. Total & status-wise count of trips
    all_trips = session.query(Trip).all()
    active_trips_count = sum(1 for t in all_trips if t.status == TripStatus.ongoing)
    pending_trips_count = sum(1 for t in all_trips if t.status == TripStatus.scheduled)
    
    # 2. Fleet Utilization
    vehicles = session.query(Vehicle).all()
    total_vehicles = len(vehicles)
    active_vehicles = sum(1 for v in vehicles if v.status == VehicleStatus.on_trip)
    utilization_rate = round((active_vehicles / total_vehicles * 100), 1) if total_vehicles > 0 else 0.0
    
    # 3. Fleet distribution details
    available_v = sum(1 for v in vehicles if v.status == VehicleStatus.available)
    ontrip_v = active_vehicles
    inshop_v = sum(1 for v in vehicles if v.status == VehicleStatus.maintenance)
    retired_v = sum(1 for v in vehicles if v.status == VehicleStatus.retired)
    
    # 4. Recent trips list (limit 5)
    recent_trips_data = []
    sorted_trips = sorted(all_trips, key=lambda x: x.id, reverse=True)[:5]
    for t in sorted_trips:
        vehicle = session.query(Vehicle).filter_by(id=t.vehicle_id).first()
        driver = session.query(Driver).filter_by(id=t.driver_id).first()
        recent_trips_data.append({
            "id": t.id,
            "vehicle_id": vehicle.plate_number if vehicle else None,
            "driver_id": driver.name if driver else None,
            "cargo_weight": float(t.cargo_weight),
            "status": "Dispatched" if t.status == TripStatus.ongoing else ("Draft" if t.status == TripStatus.scheduled else t.status.value),
            "type": vehicle.type if vehicle else "Unknown"
        })
        
    return jsonify({
        "activeTrips": active_trips_count,
        "pendingTrips": pending_trips_count,
        "utilizationRate": f"{utilization_rate}%",
        "distribution": {
            "available": available_v,
            "on_trip": ontrip_v,
            "maintenance": inshop_v,
            "retired": retired_v,
            "total": total_vehicles
        },
        "recentTrips": recent_trips_data
    }), 200

