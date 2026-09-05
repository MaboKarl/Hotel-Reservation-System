"""
Hotel Management System - Python Backend (Procedural)
Flask REST API Server
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, Union

# Import modules
from guest_management import (
    create_guest, get_guest, update_guest, delete_guest, 
    list_guests, search_guests
)
from room_management import (
    create_room, get_room, update_room, delete_room,
    list_rooms, get_available_rooms
)
from booking_management import (
    create_booking, get_booking, cancel_booking,
    check_in, check_out, list_bookings,
    get_guest_bookings, get_current_check_ins,
    delete_booking as delete_booking_func  # FIXED: Added delete_booking
)
from payment_processing import (
    process_payment, get_payment, refund_payment, list_payments
)
from report_generation import (
    generate_occupancy_report, generate_revenue_report,
    generate_guest_report, generate_booking_report,
    generate_full_report
)
from data.hotel_data import bookings, load_data, save_data

# Import config helpers
from config import DATETIME_FORMAT, format_datetime, local_now

# Import authentication
from auth import (
    token_required, admin_required, role_required, login_user,
    get_current_user, get_or_create_guest_id
)

# FIXED #18: Import sanitization helpers
from utils.validators import (
    sanitize_input, sanitize_email, sanitize_phone, sanitize_name,
    sanitize_text, sanitize_address, sanitize_number, sanitize_float,
    sanitize_guest_id, sanitize_room_id, sanitize_booking_id,
    sanitize_guest_count, sanitize_amount
)

# FIXED: Import error handler with proper path
from utils.error_handler import (
    ValidationError, NotFoundError, ConflictError, GuestError, 
    RoomError, BookingError, PaymentError, HotelError
)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend
load_data()


# ============================================
# STANDARDIZED RESPONSE HELPERS
# ============================================

def error_response(message: str, error_code: Optional[str] = None, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> tuple:
    """Standardized error response for all endpoints."""
    response = {
        'success': False,
        'error': message,
        'status': status_code
    }
    if error_code:
        response['error_code'] = error_code
    if details:
        response['details'] = details
    return jsonify(response), status_code


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> tuple:
    """Standardized success response for all endpoints."""
    response = {
        'success': True,
        'message': message,
        'status': status_code
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def get_room_availability(room_id: int) -> Dict[str, Any]:
    """Return date and time availability information for a room."""
    active_bookings = [
        booking for booking in bookings.values()
        if booking.get('room_id') == room_id and booking.get('status') != 'CANCELLED'
    ]
    active_bookings.sort(key=lambda booking: booking.get('check_in', ''))

    if not active_bookings:
        return {
            'available_now': True,
            'label': 'Available now',
            'next_check_in': None,
            'next_available': 'Today at 2:00 PM',
            'booked_windows': []
        }

    current = active_bookings[0]
    check_in_time = current.get('check_in_time', '14:00')
    check_out_time = current.get('check_out_time', '12:00')
    return {
        'available_now': False,
        'label': f"Booked {current['check_in']} at {check_in_time} - {current['check_out']} at {check_out_time}",
        'next_check_in': current['check_in'],
        'next_available': f"{current['check_out']} at {check_out_time}",
        'booked_windows': [
            {
                'check_in': booking['check_in'],
                'check_in_time': booking.get('check_in_time', '14:00'),
                'check_out': booking['check_out'],
                'check_out_time': booking.get('check_out_time', '12:00')
            }
            for booking in active_bookings
        ]
    }


def handle_exception(e: Exception, default_message: str = "An error occurred") -> tuple:
    """Handle any exception and return a standardized error response."""
    
    message = str(e) if str(e) else default_message
    
    if isinstance(e, NotFoundError):
        return error_response(message, 'NOT_FOUND', 404)
    elif isinstance(e, ValidationError):
        return error_response(message, 'VALIDATION_ERROR', 400)
    elif isinstance(e, ConflictError):
        return error_response(message, 'CONFLICT', 409)
    elif isinstance(e, GuestError):
        return error_response(message, 'GUEST_ERROR', 400)
    elif isinstance(e, RoomError):
        return error_response(message, 'ROOM_ERROR', 400)
    elif isinstance(e, BookingError):
        return error_response(message, 'BOOKING_ERROR', 400)
    elif isinstance(e, PaymentError):
        return error_response(message, 'PAYMENT_ERROR', 400)
    else:
        # Generic error handling
        return error_response(message, 'INTERNAL_ERROR', 500)


# ============================================
# AUTH ENDPOINTS
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT token."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize login inputs
        username = sanitize_input(data.get('username'))
        password = sanitize_input(data.get('password'))
        
        if not username or not password:
            return error_response("Username and password are required", "MISSING_CREDENTIALS", 400)
        
        result = login_user(username, password)
        
        if not result:
            return error_response("Invalid username or password", "INVALID_CREDENTIALS", 401)
        
        return success_response(result, "Login successful", 200)
        
    except Exception as e:
        return handle_exception(e, "Login failed")


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user_info():
    """Get the current authenticated user's information."""
    current_user = get_current_user()
    return success_response({
        'username': current_user.get('username'),
        'role': current_user.get('role')
    }, "User info retrieved successfully")


@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token():
    """Verify that a token is valid."""
    current_user = get_current_user()
    return success_response({
        'username': current_user.get('username'),
        'role': current_user.get('role'),
        'valid': True
    }, "Token is valid")


# ============================================
# GUEST ENDPOINTS - FIXED #18: Input Sanitization
# ============================================

@app.route('/api/guests', methods=['GET'])
@token_required
def get_guests():
    """Get all guests"""
    try:
        guests = list_guests()
        return success_response(guests, "Guests retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve guests")


@app.route('/api/guests', methods=['POST'])
@token_required
def add_guest():
    """Create a new guest - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize all inputs
        first_name = sanitize_name(data.get('firstName'))
        last_name = sanitize_name(data.get('lastName'))
        email = sanitize_email(data.get('email'))
        phone = sanitize_phone(data.get('phone'))
        address = sanitize_address(data.get('address', ''))
        
        guest = create_guest(first_name, last_name, email, phone, address)
        return success_response(guest, "Guest created successfully", 201)
    except Exception as e:
        return handle_exception(e, "Failed to create guest")


@app.route('/api/guests/<int:guest_id>', methods=['GET'])
@token_required
def get_guest_by_id(guest_id):
    """Get guest by ID"""
    try:
        # FIXED #18: Sanitize guest_id
        sanitized_id = sanitize_guest_id(guest_id)
        guest = get_guest(sanitized_id)
        return success_response(guest, "Guest retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve guest")


@app.route('/api/guests/<int:guest_id>', methods=['PUT'])
@token_required
def update_guest_by_id(guest_id):
    """Update guest - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize guest_id
        sanitized_id = sanitize_guest_id(guest_id)
        
        # FIXED #18: Sanitize all inputs
        updates = {}
        if 'firstName' in data:
            updates['first_name'] = sanitize_name(data['firstName'])
        if 'lastName' in data:
            updates['last_name'] = sanitize_name(data['lastName'])
        if 'email' in data:
            updates['email'] = sanitize_email(data['email'])
        if 'phone' in data:
            updates['phone'] = sanitize_phone(data['phone'])
        if 'address' in data:
            updates['address'] = sanitize_address(data['address'])
        
        guest = update_guest(sanitized_id, **updates)
        return success_response(guest, "Guest updated successfully")
    except Exception as e:
        return handle_exception(e, "Failed to update guest")


@app.route('/api/guests/<int:guest_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_guest_by_id(guest_id):
    """Delete guest"""
    try:
        # FIXED #18: Sanitize guest_id
        sanitized_id = sanitize_guest_id(guest_id)
        delete_guest(sanitized_id)
        return success_response(None, "Guest deleted successfully", 200)
    except Exception as e:
        return handle_exception(e, "Failed to delete guest")


@app.route('/api/guests/search', methods=['GET'])
@token_required
def search_guests_endpoint():
    """Search guests - FIXED #18: Sanitized search term"""
    try:
        # FIXED #18: Sanitize search term
        search_term = sanitize_text(request.args.get('q', ''))
        results = search_guests(search_term)
        return success_response(results, f"Found {len(results)} guests matching '{search_term}'")
    except Exception as e:
        return handle_exception(e, "Failed to search guests")


# ============================================
# ROOM ENDPOINTS - FIXED #18: Input Sanitization
# ============================================

@app.route('/api/rooms', methods=['GET'])
@token_required
def get_rooms():
    """Get all rooms"""
    try:
        rooms = list_rooms()
        room_results = {}
        for room_id, room in rooms.items():
            room_copy = room.copy()
            room_copy['availability'] = get_room_availability(room_id)
            room_results[room_id] = room_copy
        return success_response(room_results, "Rooms retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve rooms")


@app.route('/api/rooms', methods=['POST'])
@token_required
@admin_required
def add_room():
    """Create a new room - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize inputs
        room_number = sanitize_number(data.get('roomNumber'))
        room_type = sanitize_input(data.get('roomType')).upper()
        floor = sanitize_number(data.get('floor'))
        image_url = sanitize_input(data.get('imageUrl', ''))
        details = sanitize_text(data.get('details', ''), max_length=1000)
        name = sanitize_text(data.get('name', ''), max_length=120)
        
        if room_number <= 0:
            return error_response("Room number must be positive", "INVALID_ROOM_NUMBER", 400)
        if floor <= 0:
            return error_response("Floor must be positive", "INVALID_FLOOR", 400)
        
        room = create_room(room_number, room_type, floor, image_url, details, name)
        return success_response(room, "Room created successfully", 201)
    except Exception as e:
        return handle_exception(e, "Failed to create room")


@app.route('/api/rooms/available', methods=['GET'])
@token_required
def get_available_rooms_endpoint():
    """Get available rooms - FIXED #18: Sanitized room type"""
    try:
        # FIXED #18: Sanitize room type
        room_type = sanitize_input(request.args.get('type', ''))
        if not room_type:
            room_type = None
        else:
            room_type = room_type.upper()
        
        rooms = get_available_rooms(room_type)
        return success_response(rooms, "Available rooms retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve available rooms")


@app.route('/api/rooms/<int:room_id>', methods=['GET'])
@token_required
def get_room_by_id(room_id):
    """Get room by ID"""
    try:
        # FIXED #18: Sanitize room_id
        sanitized_id = sanitize_room_id(room_id)
        room = get_room(sanitized_id)
        return success_response(room, "Room retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve room")


@app.route('/api/rooms/<int:room_id>', methods=['PUT'])
@token_required
@admin_required
def update_room_by_id(room_id):
    """Update room - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize room_id
        sanitized_id = sanitize_room_id(room_id)
        
        # FIXED #18: Sanitize inputs
        updates = {}
        if 'room_type' in data:
            updates['room_type'] = sanitize_input(data['room_type']).upper()
        if 'status' in data:
            updates['status'] = sanitize_input(data['status']).upper()
        if 'imageUrl' in data:
            updates['image_url'] = sanitize_input(data['imageUrl'])
        if 'details' in data:
            updates['details'] = sanitize_text(data['details'], max_length=1000)
        if 'name' in data:
            updates['name'] = sanitize_text(data['name'], max_length=120)
        
        room = update_room(sanitized_id, **updates)
        return success_response(room, "Room updated successfully")
    except Exception as e:
        return handle_exception(e, "Failed to update room")


@app.route('/api/rooms/<int:room_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_room_by_id(room_id):
    """Delete room"""
    try:
        # FIXED #18: Sanitize room_id
        sanitized_id = sanitize_room_id(room_id)
        delete_room(sanitized_id)
        return success_response(None, "Room deleted successfully", 200)
    except Exception as e:
        return handle_exception(e, "Failed to delete room")


# ============================================
# BOOKING ENDPOINTS - FIXED #18: Input Sanitization
# ============================================

@app.route('/api/bookings', methods=['GET'])
@token_required
def get_bookings():
    """Get all bookings"""
    try:
        bookings = list_bookings()
        return success_response(bookings, "Bookings retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve bookings")


@app.route('/api/bookings', methods=['POST'])
@token_required
def add_booking():
    """Create a new booking - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize all inputs
        current_user = get_current_user()
        if current_user.get('role') == 'user':
            guest_id = get_or_create_guest_id(current_user['username'])
        else:
            guest_id = sanitize_guest_id(data.get('guestId'))
        room_id = sanitize_room_id(data.get('roomId'))
        check_in = sanitize_input(data.get('checkIn'))
        check_out = sanitize_input(data.get('checkOut'))
        check_in_time = sanitize_input(data.get('checkInTime', '14:00'))
        check_out_time = sanitize_input(data.get('checkOutTime', '12:00'))
        guest_count = sanitize_guest_count(data.get('guestCount', 1))
        special_requests = sanitize_text(data.get('specialRequests', ''))
        
        booking = create_booking(
            guest_id, room_id, check_in, check_out, guest_count, special_requests,
            check_in_time, check_out_time
        )
        return success_response(booking, "Booking created successfully", 201)
    except Exception as e:
        return handle_exception(e, "Failed to create booking")


@app.route('/api/bookings/check-in', methods=['POST'])
@token_required
def check_in_guest():
    """Check in a guest - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize booking_id
        booking_id = sanitize_booking_id(data.get('bookingId'))
        
        booking = check_in(booking_id)
        return success_response(booking, "Guest checked in successfully")
    except Exception as e:
        return handle_exception(e, "Failed to check in guest")


@app.route('/api/bookings/check-out', methods=['POST'])
@token_required
def check_out_guest():
    """Check out a guest - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize booking_id
        booking_id = sanitize_booking_id(data.get('bookingId'))
        
        booking = check_out(booking_id)
        return success_response(booking, "Guest checked out successfully")
    except Exception as e:
        return handle_exception(e, "Failed to check out guest")


@app.route('/api/bookings/cancel', methods=['POST'])
@token_required
def cancel_booking_endpoint():
    """Cancel a booking - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize booking_id
        booking_id = sanitize_booking_id(data.get('bookingId'))
        
        booking = cancel_booking(booking_id)
        return success_response(booking, "Booking cancelled successfully")
    except Exception as e:
        return handle_exception(e, "Failed to cancel booking")


@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
@token_required
def get_booking_by_id(booking_id):
    """Get booking by ID"""
    try:
        # FIXED #18: Sanitize booking_id
        sanitized_id = sanitize_booking_id(booking_id)
        booking = get_booking(sanitized_id)
        return success_response(booking, "Booking retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve booking")


@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_booking_by_id(booking_id):
    """Delete a booking - FIXED #19"""
    try:
        # FIXED #18: Sanitize booking_id
        sanitized_id = sanitize_booking_id(booking_id)
        result = delete_booking_func(sanitized_id)
        return success_response(result, "Booking deleted successfully", 200)
    except Exception as e:
        return handle_exception(e, "Failed to delete booking")


@app.route('/api/bookings/current', methods=['GET'])
@token_required
def get_current_check_ins_endpoint():
    """Get current check-ins"""
    try:
        checkins = get_current_check_ins()
        return success_response(checkins, "Current check-ins retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve current check-ins")


@app.route('/api/bookings/guest/<int:guest_id>', methods=['GET'])
@token_required
def get_guest_bookings_endpoint(guest_id):
    """Get bookings for a guest"""
    try:
        # FIXED #18: Sanitize guest_id
        sanitized_id = sanitize_guest_id(guest_id)
        bookings = get_guest_bookings(sanitized_id)
        return success_response(bookings, "Guest bookings retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve guest bookings")


# ============================================
# PAYMENT ENDPOINTS - FIXED #18: Input Sanitization
# ============================================

@app.route('/api/payments', methods=['GET'])
@token_required
def get_payments():
    """Get all payments"""
    try:
        payments = list_payments()
        return success_response(payments, "Payments retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve payments")


@app.route('/api/payments', methods=['POST'])
@token_required
def add_payment():
    """Process a payment - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize all inputs
        booking_id = sanitize_booking_id(data.get('bookingId'))
        amount = sanitize_amount(data.get('amount'))
        payment_method = sanitize_input(data.get('paymentMethod', 'Credit Card'))
        
        payment = process_payment(booking_id, amount, payment_method)
        return success_response(payment, "Payment processed successfully", 201)
    except Exception as e:
        return handle_exception(e, "Failed to process payment")


@app.route('/api/payments/<int:payment_id>', methods=['GET'])
@token_required
def get_payment_by_id(payment_id):
    """Get payment by ID"""
    try:
        # FIXED #18: Sanitize payment_id
        sanitized_id = sanitize_number(payment_id)
        if sanitized_id <= 0:
            return error_response("Invalid payment ID", "INVALID_PAYMENT_ID", 400)
        
        payment = get_payment(sanitized_id)
        return success_response(payment, "Payment retrieved successfully")
    except Exception as e:
        return handle_exception(e, "Failed to retrieve payment")


@app.route('/api/payments/refund', methods=['POST'])
@token_required
@admin_required
def refund_payment_endpoint():
    """Refund a payment - FIXED #18: Sanitized inputs"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Request body is required", "MISSING_BODY", 400)
        
        # FIXED #18: Sanitize payment_id
        payment_id = sanitize_number(data.get('paymentId'))
        if payment_id <= 0:
            return error_response("Invalid payment ID", "INVALID_PAYMENT_ID", 400)
        
        payment = refund_payment(payment_id)
        return success_response(payment, "Payment refunded successfully")
    except Exception as e:
        return handle_exception(e, "Failed to refund payment")


# ============================================
# REPORT ENDPOINTS
# ============================================

@app.route('/api/reports/occupancy', methods=['GET'])
@token_required
def get_occupancy_report():
    """Get occupancy report"""
    try:
        report = generate_occupancy_report()
        return success_response(report, "Occupancy report generated successfully")
    except Exception as e:
        return handle_exception(e, "Failed to generate occupancy report")


@app.route('/api/reports/revenue', methods=['GET'])
@token_required
@admin_required
def get_revenue_report():
    """Get revenue report - FIXED #18: Sanitized date inputs"""
    try:
        # FIXED #18: Sanitize date inputs
        start_date = sanitize_input(request.args.get('start_date', ''))
        end_date = sanitize_input(request.args.get('end_date', ''))
        
        report = generate_revenue_report(start_date if start_date else None, end_date if end_date else None)
        return success_response(report, "Revenue report generated successfully")
    except Exception as e:
        return handle_exception(e, "Failed to generate revenue report")


@app.route('/api/reports/guests', methods=['GET'])
@token_required
def get_guest_report():
    """Get guest report"""
    try:
        report = generate_guest_report()
        return success_response(report, "Guest report generated successfully")
    except Exception as e:
        return handle_exception(e, "Failed to generate guest report")


@app.route('/api/reports/bookings', methods=['GET'])
@token_required
def get_booking_report():
    """Get booking report"""
    try:
        report = generate_booking_report()
        return success_response(report, "Booking report generated successfully")
    except Exception as e:
        return handle_exception(e, "Failed to generate booking report")


@app.route('/api/reports/full', methods=['GET'])
@token_required
@admin_required
def get_full_report():
    """Get full report"""
    try:
        report = generate_full_report()
        return success_response(report, "Full report generated successfully")
    except Exception as e:
        return handle_exception(e, "Failed to generate full report")


# ============================================
# HEALTH CHECK - Public endpoint (no auth required)
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint - public"""
    return success_response({
        'status': 'healthy',
        'backend': 'Python (Procedural)',
        'timestamp': format_datetime(local_now()),
        'auth_required': True
    }, "Health check passed", 200)


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("Starting Python Hotel Management System (Procedural)...")
    print("Server running on http://localhost:5000")
    print("")
    print("Default Users:")
    print("  admin / admin123 (admin role)")
    print("  user / user123 (user role)")
    print("")
    print("Use /api/auth/login to get a token")
    print("Add 'Authorization: Bearer <token>' header to authenticated requests")
    app.run(debug=True, port=5000)