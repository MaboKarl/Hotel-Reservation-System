"""
Authentication Module - JWT-based authentication
"""

import jwt
import re
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any
from flask import request, jsonify

from config import DATETIME_FORMAT, format_datetime
from data.hotel_data import guests, get_next_id, save_data

# Secret key - In production, use environment variable
SECRET_KEY = 'your-secret-key-change-this-in-production'
ALGORITHM = 'HS256'
TOKEN_EXPIRY_DAYS = 7

# User database (in production, use a real database)
# FIXED #17: Hardcoded users for demo - in production, store in database
USERS = {
    'admin': {
        'password': 'admin123',  # In production, store hashed passwords!
        'role': 'admin'
    },
    'user': {
        'password': 'user123',
        'role': 'user'
    }
}


def generate_token(username: str, role: str) -> str:
    """
    Generate a JWT token for a user.
    
    Args:
        username: Username
        role: User role ('admin' or 'user')
    
    Returns:
        str: JWT token
    
    Example:
        >>> token = generate_token('admin', 'admin')
        >>> len(token) > 0
        True
    """
    payload = {
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=TOKEN_EXPIRY_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token
    
    Returns:
        Optional[Dict[str, Any]]: Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """
    Decorator to require authentication for an endpoint.
    
    Usage:
        @app.route('/api/protected')
        @token_required
        def protected_endpoint(current_user):
            return jsonify({'message': f'Hello {current_user["username"]}'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'Authorization token is missing',
                'error_code': 'MISSING_TOKEN',
                'status': 401
            }), 401
        
        # Check if header is in format "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'success': False,
                'error': 'Invalid Authorization header format. Use Bearer <token>',
                'error_code': 'INVALID_AUTH_FORMAT',
                'status': 401
            }), 401
        
        token = parts[1]
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token',
                'error_code': 'INVALID_TOKEN',
                'status': 401
            }), 401
        
        # Add current user to request context
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    Decorator to require admin role for an endpoint.
    Must be used after @token_required.
    
    Usage:
        @app.route('/api/admin-only')
        @token_required
        @admin_required
        def admin_endpoint():
            return jsonify({'message': 'Admin only'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = getattr(request, 'current_user', None)
        
        if not current_user:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'error_code': 'AUTH_REQUIRED',
                'status': 401
            }), 401
        
        if current_user.get('role') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin privileges required',
                'error_code': 'ADMIN_REQUIRED',
                'status': 403
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated


def role_required(allowed_roles: list):
    """
    Decorator to require specific role(s) for an endpoint.
    Must be used after @token_required.
    
    Args:
        allowed_roles: List of allowed roles
    
    Usage:
        @app.route('/api/restricted')
        @token_required
        @role_required(['admin', 'manager'])
        def restricted_endpoint():
            return jsonify({'message': 'Access granted'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = getattr(request, 'current_user', None)
            
            if not current_user:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'error_code': 'AUTH_REQUIRED',
                    'status': 401
                }), 401
            
            if current_user.get('role') not in allowed_roles:
                return jsonify({
                    'success': False,
                    'error': f'Role {current_user.get("role")} not authorized. Required: {allowed_roles}',
                    'error_code': 'ROLE_NOT_AUTHORIZED',
                    'status': 403
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator


def login_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user and generate a token.
    
    Args:
        username: Username
        password: Password
    
    Returns:
        Optional[Dict[str, Any]]: Token and user info if authenticated, None otherwise
    
    Example:
        >>> result = login_user('admin', 'admin123')
        >>> result['token']
        'eyJhbGciOiJIUzI1NiIs...'
    """
    user = USERS.get(username)
    
    if not user:
        return None
    
    # In production, use hashed password comparison
    if user['password'] != password:
        return None
    
    token = generate_token(username, user['role'])

    guest_id = get_or_create_guest_id(username) if user['role'] == 'user' else None
    
    result = {
        'token': token,
        'username': username,
        'role': user['role'],
        'expires_in': TOKEN_EXPIRY_DAYS * 24 * 60 * 60  # seconds
    }
    if guest_id is not None:
        result['guest_id'] = guest_id
    return result


def get_or_create_guest_id(username: str) -> int:
    """Return the guest record linked to a user login, creating it if needed."""
    guest_email = f'{username}@example.com'
    for existing_id, guest in guests.items():
        if guest.get('email', '').lower() == guest_email:
            return existing_id

    guest_id = get_next_id('guest')
    guests[guest_id] = {
        'guest_id': guest_id,
        'first_name': username.capitalize(),
        'last_name': 'Guest',
        'email': guest_email,
        'phone': '09171234567',
        'address': '',
        'bookings': []
    }
    save_data()
    return guest_id


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from the request context.
    
    Returns:
        Optional[Dict[str, Any]]: User info if authenticated, None otherwise
    """
    return getattr(request, 'current_user', None)