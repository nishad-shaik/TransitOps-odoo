import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from app.config import Config
from app.database import SessionLocal
from app.models import User, UserRole

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Email and password are required"}}), 400

    session = SessionLocal()
    user = session.query(User).filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Invalid email or password"}}), 401

    if not user.is_active:
        return jsonify({"error": {"code": "FORBIDDEN", "message": "User account is suspended"}}), 403

    token = jwt.encode(
        {
            'sub': str(user.id),
            'email': user.email,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(days=1)
        },
        Config.SECRET_KEY,
        algorithm='HS256'
    )

    return jsonify({
        "token": token,
        "user": {
            "email": user.email,
            "role": user.role.value
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    role_str = data.get('role', 'Driver')

    if not email or not password:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Email and password are required"}}), 400

    session = SessionLocal()
    existing = session.query(User).filter_by(email=email).first()
    if existing:
        return jsonify({"error": {"code": "CONFLICT", "message": "Email already registered"}}), 409

    try:
        role = UserRole(role_str)
    except ValueError:
        role = UserRole.driver

    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        is_active=True
    )
    session.add(new_user)
    session.commit()

    return jsonify({"message": "Registration successful", "email": email}), 201
