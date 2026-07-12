import jwt
from functools import wraps
from flask import request, g
from app.config import Config
from app.utils import unauthorized, forbidden

def token_required(f):
    """Decorator to enforce valid JWT token verification and inject user context."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return unauthorized("Authentication token is missing")
            
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            g.user_email = data.get('email')
            g.user_role = data.get('role')
        except jwt.ExpiredSignatureError:
            return unauthorized("Token has expired")
        except jwt.InvalidTokenError:
            return unauthorized("Token is invalid or malformed")
            
        return f(*args, **kwargs)
    return decorated

def roles_accepted(*roles):
    """Decorator to restrict access to specific user roles (RBAC)."""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if not g.user_role or g.user_role not in roles:
                return forbidden(f"Access denied: role '{g.user_role}' is not authorized to perform this action")
            return f(*args, **kwargs)
        return decorated
    return decorator
