from flask import request, jsonify
from app.utils import parse_date, bad_request

@app.route('/maintenance', methods=['POST'])
def create_maintenance():
    data = request.get_json()
    start_date = parse_date(data.get('start_date'))
    
    if not start_date:
        return bad_request("Invalid or missing start_date")
    return jsonify({"message": "Maintenance created"}), 201