from datetime import datetime
from flask import jsonify

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def bad_request(message):
    return jsonify({
        "error": {
            "code": "BAD_REQUEST",
            "message": message
        }
    }), 400

def unauthorized(message="Authentication required"):
    return jsonify({
        "error": {
            "code": "UNAUTHORIZED",
            "message": message
        }
    }), 401

def forbidden(message="Access denied"):
    return jsonify({
        "error": {
            "code": "FORBIDDEN",
            "message": message
        }
    }), 403

def not_found(message="Resource not found"):
    return jsonify({
        "error": {
            "code": "NOT_FOUND",
            "message": message
        }
    }), 404