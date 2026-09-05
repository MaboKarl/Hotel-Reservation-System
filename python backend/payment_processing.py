"""
Payment Processing Module - Procedural
"""

from datetime import datetime
from data.hotel_data import payments, bookings, get_next_id, save_data
from room_management import update_room_status
from utils.validators import validate_positive_number
from utils.error_handler import PaymentError, ValidationError
from config import local_now

# NOTE: booking_management import is removed to break circular dependency
# get_booking() is imported lazily inside functions that need it


def get_booking(booking_id):
    """
    Lazy import to avoid circular dependency with booking_management
    
    This function imports get_booking from booking_management only when called,
    breaking the circular dependency between this module and booking_management.
    """
    from booking_management import get_booking as _get_booking
    return _get_booking(booking_id)


def process_payment(booking_id, amount, payment_method="Credit Card"):
    """Process a payment"""
    booking = get_booking(booking_id)
    
    if booking.get('payment_id'):
        raise PaymentError("Payment already exists for this booking")
    
    if booking['status'] == 'CANCELLED':
        raise PaymentError("Cannot process payment for a cancelled booking")
    
    is_valid, message = validate_positive_number(amount, "Payment amount")
    if not is_valid:
        raise ValidationError(message)
    
    amount = float(amount)
    if abs(amount - booking['total_amount']) > 0.01:
        raise PaymentError(f"Payment amount {amount} does not match booking total {booking['total_amount']}")
    
    valid_methods = ['Credit Card', 'Cash', 'Bank Transfer', 'GCash', 'PayPal']
    if payment_method not in valid_methods:
        raise ValidationError(f"Invalid payment method: {payment_method}")
    
    payment_id = get_next_id('payment')
    payment_data = {
        'payment_id': payment_id,
        'booking_id': booking_id,
        'amount': amount,
        'payment_method': payment_method,
        'status': 'PAID',
        'transaction_date': local_now().strftime('%Y-%m-%d %H:%M:%S'),
        'refund_date': None
    }
    
    payments[payment_id] = payment_data
    
    # Update booking
    booking['payment_id'] = payment_id
    bookings[booking_id] = booking
    update_room_status(booking['room_id'], 'CLEANING')
    
    save_data()
    return payment_data


def refund_payment(payment_id):
    """Refund a payment"""
    payment = get_payment(payment_id)
    
    if payment['status'] == 'REFUNDED':
        raise PaymentError("Payment has already been refunded")
    
    if payment['status'] != 'PAID':
        raise PaymentError(f"Cannot refund a payment with status: {payment['status']}")
    
    payment['status'] = 'REFUNDED'
    payment['refund_date'] = local_now().strftime('%Y-%m-%d %H:%M:%S')
    payments[payment_id] = payment
    
    # Update booking
    booking = get_booking(payment['booking_id'])
    booking['payment_id'] = None
    bookings[booking['booking_id']] = booking  # FIXED: Use booking_id from booking dict
    
    save_data()
    return payment


def get_payment(payment_id):
    """Get payment by ID"""
    try:
        payment_id = int(payment_id)
    except (ValueError, TypeError):
        raise ValidationError("Invalid payment ID format")
    
    payment = payments.get(payment_id)
    if not payment:
        raise PaymentError(f"Payment with ID {payment_id} not found")
    return payment


def list_payments():
    """List all payments"""
    return payments


def get_booking_payment(booking_id):
    """Get payment for a booking"""
    booking = get_booking(booking_id)
    if not booking.get('payment_id'):
        return None
    return get_payment(booking['payment_id'])


# ============================================
# FIXED: Helper functions to reduce coupling
# ============================================

def has_booking_payment(booking_id):
    """Check if a booking has a payment"""
    booking = get_booking(booking_id)
    return booking.get('payment_id') is not None


def get_booking_payment_id(booking_id):
    """Get payment ID for a booking"""
    booking = get_booking(booking_id)
    return booking.get('payment_id')


def update_booking_payment(booking_id, payment_id):
    """Update booking's payment ID"""
    booking = get_booking(booking_id)
    booking['payment_id'] = payment_id
    bookings[booking['booking_id']] = booking
    save_data()
    return booking


def clear_booking_payment(booking_id):
    """Clear payment reference from booking"""
    booking = get_booking(booking_id)
    booking['payment_id'] = None
    bookings[booking['booking_id']] = booking
    save_data()
    return booking