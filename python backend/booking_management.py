"""
Booking Management Module - Procedural
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from data.hotel_data import bookings, get_next_id, save_data
from guest_management import get_guest, add_booking_to_guest
from room_management import get_room, add_booking_to_room, set_current_booking, clear_current_booking
from config import ROOM_TYPES, BOOKING_STATUSES, TAX_RATE, SERVICE_CHARGE_RATE
from config import DATE_FORMAT, DATETIME_FORMAT, format_datetime, local_now, parse_date
from utils.validators import validate_dates, validate_guest_count, sanitize_input
from utils.error_handler import BookingError, ValidationError, NotFoundError

# NOTE: payment_processing import is removed to break circular dependency
# Payment functions are imported lazily inside cancel_booking()


def calculate_booking_cost(room_type: str, check_in: str, check_out: str) -> Dict[str, Any]:
    """Calculate total cost for a booking"""
    if room_type not in ROOM_TYPES:
        raise ValidationError(f"Invalid room type: {room_type}")
    
    check_in_date = parse_date(check_in)
    check_out_date = parse_date(check_out)
    
    nights = (check_out_date - check_in_date).days
    room_price = ROOM_TYPES[room_type]['base_price']
    
    subtotal = room_price * nights
    tax = subtotal * TAX_RATE
    service_charge = subtotal * SERVICE_CHARGE_RATE
    total = subtotal + tax + service_charge
    
    return {
        'nights': nights,
        'room_price': room_price,
        'subtotal': subtotal,
        'tax': tax,
        'service_charge': service_charge,
        'total': total
    }


def _booking_interval(check_in: str, check_out: str, check_in_time: str = '14:00', check_out_time: str = '12:00'):
    """Build a comparable date-time interval for a reservation."""
    try:
        start = datetime.strptime(f'{check_in} {check_in_time}', '%Y-%m-%d %H:%M')
        end = datetime.strptime(f'{check_out} {check_out_time}', '%Y-%m-%d %H:%M')
    except ValueError:
        raise ValidationError('Invalid booking time. Use HH:MM format.')
    if end <= start:
        raise ValidationError('Checkout time must be after check-in time.')
    return start, end


def _room_has_overlapping_booking(room_id: int, start: datetime, end: datetime) -> bool:
    """Return whether a room has an active booking overlapping an interval."""
    for booking in bookings.values():
        if booking.get('room_id') != room_id or booking.get('status') == 'CANCELLED':
            continue
        booking_start, booking_end = _booking_interval(
            booking['check_in'],
            booking['check_out'],
            booking.get('check_in_time', '14:00'),
            booking.get('check_out_time', '12:00')
        )
        if start < booking_end and end > booking_start:
            return True
    return False


def create_booking(
    guest_id: Union[int, str],
    room_id: Union[int, str],
    check_in: str,
    check_out: str,
    guest_count: int = 1,
    special_requests: str = "",
    check_in_time: str = '14:00',
    check_out_time: str = '12:00'
) -> Dict[str, Any]:
    """Create a new booking"""
    guest = get_guest(guest_id)
    room = get_room(room_id)
    special_requests = sanitize_input(special_requests)
    
    is_valid, message = validate_dates(check_in, check_out)
    if not is_valid:
        raise ValidationError(message)
    
    is_valid, message = validate_guest_count(guest_count)
    if not is_valid:
        raise ValidationError(message)
    
    start, end = _booking_interval(check_in, check_out, check_in_time, check_out_time)
    if _room_has_overlapping_booking(int(room_id), start, end):
        raise BookingError("Room is already booked during the selected date and time")
    
    # Check capacity
    room_type = room['room_type']
    max_guests = ROOM_TYPES[room_type]['capacity']
    if guest_count > max_guests:
        raise BookingError(f"Room type {room_type} can only accommodate {max_guests} guests")
    
    cost_breakdown = calculate_booking_cost(room_type, check_in, check_out)
    
    booking_id = get_next_id('booking')
    booking_data = {
        'booking_id': booking_id,
        'guest_id': guest_id,
        'room_id': room_id,
        'room_number': room['room_number'],
        'room_type': room_type,
        'check_in': check_in,
        'check_out': check_out,
        'check_in_time': check_in_time,
        'check_out_time': check_out_time,
        'guest_count': guest_count,
        'special_requests': special_requests,
        'status': 'CONFIRMED',
        'cost_breakdown': cost_breakdown,
        'total_amount': cost_breakdown['total'],
        'payment_id': None,
        'created_at': format_datetime(local_now())
    }
    
    bookings[booking_id] = booking_data
    add_booking_to_room(room_id, booking_id)
    now = local_now()
    if start <= now < end:
        set_current_booking(room_id, booking_id)
    add_booking_to_guest(guest_id, booking_id)
    
    save_data()
    return booking_data


def get_booking(booking_id: Union[int, str]) -> Dict[str, Any]:
    """Get booking by ID"""
    try:
        booking_id = int(booking_id)
    except (ValueError, TypeError):
        raise ValidationError("Invalid booking ID format")
    
    booking = bookings.get(booking_id)
    if not booking:
        raise NotFoundError("Booking", booking_id)
    return booking


def cancel_booking(booking_id: Union[int, str]) -> Dict[str, Any]:
    """Cancel a booking"""
    booking = get_booking(booking_id)
    
    if booking['status'] == 'CHECKED_OUT':
        raise BookingError("Cannot cancel a booking that has been checked out")
    
    if booking['status'] == 'CANCELLED':
        raise BookingError("Booking is already cancelled")
    
    if booking['status'] == 'CHECKED_IN':
        raise BookingError("Cannot cancel a booking that has been checked in")

    if booking.get('payment_id'):
        raise BookingError("Cannot cancel a booking that has already been paid. Refund the payment first.")
    
    booking['status'] = 'CANCELLED'
    bookings[booking_id] = booking
    
    # Update room only when this booking is the room's active booking.
    room = get_room(booking['room_id'])
    if room.get('current_booking') == booking_id:
        clear_current_booking(booking['room_id'])
    
    # Process refund if payment exists
    if booking['payment_id']:
        try:
            from payment_processing import refund_payment
            refund_payment(booking['payment_id'])
        except ImportError as e:
            # Fallback: just mark payment as refunded manually
            from data.hotel_data import payments, save_data as save
            from config import format_datetime
            payment = payments.get(booking['payment_id'])
            if payment:
                payment['status'] = 'REFUNDED'
                payment['refund_date'] = format_datetime(local_now())
                payments[booking['payment_id']] = payment
                save()
            raise BookingError(f"Could not process refund: {e}")
    
    save_data()
    return booking


def check_in(booking_id: Union[int, str]) -> Dict[str, Any]:
    """Check in a guest"""
    booking = get_booking(booking_id)
    
    if booking['status'] == 'CHECKED_IN':
        raise BookingError("Booking is already checked in")
    
    if booking['status'] == 'CANCELLED':
        raise BookingError("Cannot check in a cancelled booking")
    
    if booking['status'] == 'CHECKED_OUT':
        raise BookingError("Booking has already been checked out")
    
    check_in_date = parse_date(booking['check_in'])
    if check_in_date > local_now():
        raise BookingError("Cannot check in before the check-in date")
    
    booking['status'] = 'CHECKED_IN'
    bookings[booking_id] = booking
    save_data()
    return booking


def check_out(booking_id: Union[int, str]) -> Dict[str, Any]:
    """Check out a guest"""
    booking = get_booking(booking_id)
    
    if booking['status'] == 'CHECKED_OUT':
        raise BookingError("Booking is already checked out")
    
    if booking['status'] != 'CHECKED_IN':
        raise BookingError(f"Cannot check out a booking with status: {booking['status']}")
    
    booking['status'] = 'CHECKED_OUT'
    bookings[booking_id] = booking
    
    # Clear room
    clear_current_booking(booking['room_id'])
    
    save_data()
    return booking


def list_bookings() -> Dict[int, Dict[str, Any]]:
    """List all bookings"""
    return bookings.copy()


def get_guest_bookings(guest_id: Union[int, str]) -> Dict[int, Dict[str, Any]]:
    """Get bookings for a guest"""
    guest = get_guest(guest_id)
    guest_bookings = {}
    for booking_id in guest['bookings']:
        guest_bookings[booking_id] = get_booking(booking_id)
    return guest_bookings


def get_current_check_ins() -> List[Dict[str, Any]]:
    """Get all current check-ins"""
    current = []
    for booking_id, booking in bookings.items():
        if booking['status'] == 'CHECKED_IN':
            guest = get_guest(booking['guest_id'])
            current.append({
                'booking_id': booking_id,
                'guest_name': f"{guest['first_name']} {guest['last_name']}",
                'room_number': booking['room_number'],
                'check_out': booking['check_out']
            })
    return current


# ============================================
# FIXED #19: Booking Deletion with Cleanup
# ============================================

def delete_booking(booking_id: Union[int, str]) -> bool:
    """
    Delete a booking and clean up all references.
    
    FIXED #19: Properly clean up:
    1. Remove booking from guest's booking list
    2. Remove booking from room's booking list
    3. If it was current booking, clear it
    4. Remove payment reference if exists
    5. Delete the booking record
    
    Args:
        booking_id: Booking ID to delete
    
    Returns:
        bool: True if deleted successfully
    
    Raises:
        NotFoundError: If booking not found
        BookingError: If booking has active check-in
    
    Example:
        >>> delete_booking(101)
        True
    """
    booking = get_booking(booking_id)
    
    # Don't allow deletion of checked-in bookings
    if booking['status'] == 'CHECKED_IN':
        raise BookingError(
            "Cannot delete a booking that is currently checked in",
            details={'booking_id': booking_id, 'status': booking['status']}
        )
    
    # Remove from guest
    guest_id = booking['guest_id']
    from data.hotel_data import guests as guest_data
    try:
        guest = guest_data.get(guest_id)
        if guest and booking_id in guest.get('bookings', []):
            guest['bookings'].remove(booking_id)
            guest_data[guest_id] = guest
    except Exception:
        pass
    
    # Remove from room
    room_id = booking['room_id']
    from data.hotel_data import rooms as room_data
    try:
        room = room_data.get(room_id)
        if room and booking_id in room.get('bookings', []):
            room['bookings'].remove(booking_id)
            if room.get('current_booking') == booking_id:
                room['current_booking'] = None
                if room['status'] == 'BOOKED':
                    room['status'] = 'AVAILABLE'
            room_data[room_id] = room
    except Exception:
        pass
    
    # Clear payment reference
    if booking.get('payment_id'):
        from data.hotel_data import payments as payment_data
        payment_id = booking['payment_id']
        if payment_id in payment_data:
            payment_data[payment_id]['status'] = 'ORPHANED'
            payment_data[payment_id]['notes'] = f'Orphaned from deleted booking {booking_id}'
    
    # Delete the booking
    if booking_id in bookings:
        del bookings[booking_id]
    
    save_data()
    return True


def cleanup_orphaned_booking_references() -> Dict[str, int]:
    """
    Clean up orphaned booking references in guests and rooms.
    
    Returns:
        Dict[str, int]: Statistics of cleaned data
    """
    from data.hotel_data import guests as guest_data, rooms as room_data, save_data as save
    
    stats = {
        'guest_references_fixed': 0,
        'room_references_fixed': 0
    }
    
    # Clean guest references
    for guest_id, guest in guest_data.items():
        valid_bookings = []
        for booking_id in guest.get('bookings', []):
            if booking_id in bookings:
                valid_bookings.append(booking_id)
            else:
                stats['guest_references_fixed'] += 1
        guest['bookings'] = valid_bookings
    
    # Clean room references
    for room_id, room in room_data.items():
        valid_bookings = []
        for booking_id in room.get('bookings', []):
            if booking_id in bookings:
                valid_bookings.append(booking_id)
            else:
                stats['room_references_fixed'] += 1
        room['bookings'] = valid_bookings
        
        # Fix current_booking
        current = room.get('current_booking')
        if current and current not in bookings:
            room['current_booking'] = None
            if room['status'] == 'BOOKED':
                room['status'] = 'AVAILABLE'
    
    save()
    return stats


# ============================================
# FIXED #19: Additional helper functions
# ============================================

def has_payment(booking_id: Union[int, str]) -> bool:
    """Check if a booking has an associated payment"""
    booking = get_booking(booking_id)
    return booking.get('payment_id') is not None


def get_payment_id(booking_id: Union[int, str]) -> Optional[int]:
    """Get payment ID for a booking"""
    booking = get_booking(booking_id)
    return booking.get('payment_id')


def update_payment_id(booking_id: Union[int, str], payment_id: Optional[int]) -> Dict[str, Any]:
    """Update payment ID for a booking"""
    booking = get_booking(booking_id)
    booking['payment_id'] = payment_id
    bookings[booking_id] = booking
    save_data()
    return booking


def get_booking_by_guest(guest_id: Union[int, str]) -> List[Dict[str, Any]]:
    """Get all bookings for a guest"""
    guest = get_guest(guest_id)
    result = []
    for booking_id in guest.get('bookings', []):
        try:
            result.append(get_booking(booking_id))
        except Exception:
            continue
    return result


def get_booking_by_room(room_id: Union[int, str]) -> List[Dict[str, Any]]:
    """Get all bookings for a room"""
    room = get_room(room_id)
    result = []
    for booking_id in room.get('bookings', []):
        try:
            result.append(get_booking(booking_id))
        except Exception:
            continue
    return result


def get_booking_status_counts() -> Dict[str, int]:
    """Get counts of bookings by status"""
    counts = {status: 0 for status in BOOKING_STATUSES.keys()}
    for booking in bookings.values():
        status = booking.get('status', 'UNKNOWN')
        if status in counts:
            counts[status] += 1
        else:
            counts['UNKNOWN'] = counts.get('UNKNOWN', 0) + 1
    return counts


def get_total_revenue() -> float:
    """Get total revenue from all completed bookings"""
    total = 0.0
    for booking in bookings.values():
        if booking.get('status') in ['CHECKED_OUT', 'CONFIRMED']:
            total += booking.get('total_amount', 0)
    return round(total, 2)