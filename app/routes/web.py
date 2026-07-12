from flask import Blueprint, jsonify

web_bp = Blueprint('web', __name__)

@web_bp.route('/status', methods=['GET'])
def server_status():
    return jsonify({"status": "healthy", "service": "TransitOps API Backend"}), 200
