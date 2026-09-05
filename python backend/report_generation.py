"""
Report Generation Module - Procedural

This module generates various reports for the hotel management system:
- Occupancy reports
- Revenue reports
- Guest reports
- Booking reports
- Full system reports
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from data.hotel_data import guests, rooms, bookings, payments
from booking_management import get_booking
from room_management import get_room
from guest_management import get_guest
from config import ROOM_TYPES, local_now


# Date format constant
DATE_FORMAT: str = '%Y-%m-%d'
DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'


def generate_occupancy_report() -> Dict[str, Any]:
    """
    Generate occupancy report showing room status distribution.
    
    Returns:
        Dict[str, Any]: Report containing:
            - total_rooms: Total number of rooms
            - booked_rooms: Number of booked rooms
            - available_rooms: Number of available rooms
            - maintenance_rooms: Number of rooms under maintenance
            - cleaning_rooms: Number of rooms being cleaned
            - occupancy_rate: Percentage of rooms booked
            - room_type_stats: Breakdown by room type
    
    Example:
        >>> report = generate_occupancy_report()
        >>> report['occupancy_rate']
        37.5
        >>> report['total_rooms']
        8
    """
    total_rooms = len(rooms)
    booked_rooms = 0
    available_rooms = 0
    maintenance_rooms = 0
    cleaning_rooms = 0
    booked_guest_count = 0
    booked_room_capacity = 0
    active_room_ids = {
        booking.get('room_id')
        for booking in bookings.values()
        if booking.get('status') in ('CONFIRMED', 'CHECKED_IN')
    }
    
    room_type_stats: Dict[str, Dict[str, int]] = {}
    
    for room_id, room in rooms.items():
        room_type = room['room_type']
        
        if room_type not in room_type_stats:
            room_type_stats[room_type] = {'total': 0, 'booked': 0, 'available': 0}
        
        room_type_stats[room_type]['total'] += 1
        
        is_reserved = room_id in active_room_ids or room['status'] == 'BOOKED'
        if is_reserved:
            booked_rooms += 1
            booked_room_capacity += int(ROOM_TYPES.get(room_type, {}).get('capacity', 0))
            room_type_stats[room_type]['booked'] += 1
        elif room['status'] == 'AVAILABLE':
            available_rooms += 1
            room_type_stats[room_type]['available'] += 1
        elif room['status'] == 'MAINTENANCE':
            maintenance_rooms += 1
        elif room['status'] == 'CLEANING':
            cleaning_rooms += 1

    for booking in bookings.values():
        if booking.get('status') in ('CONFIRMED', 'CHECKED_IN'):
            booked_guest_count += int(booking.get('guest_count', 0))
    
    occupancy_rate = (booked_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    return {
        'total_rooms': total_rooms,
        'booked_rooms': booked_rooms,
        'available_rooms': available_rooms,
        'maintenance_rooms': maintenance_rooms,
        'cleaning_rooms': cleaning_rooms,
        'booked_guest_count': booked_guest_count,
        'booked_room_capacity': booked_room_capacity,
        'occupancy_rate': round(occupancy_rate, 2),
        'room_type_stats': room_type_stats,
        'generated_at': local_now().strftime(DATETIME_FORMAT)
    }


def generate_revenue_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate revenue report for a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to 30 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to today)
    
    Returns:
        Dict[str, Any]: Report containing:
            - start_date: Report start date
            - end_date: Report end date
            - total_revenue: Total revenue in period
            - bookings_count: Number of bookings in period
            - payment_methods: Breakdown by payment method
            - average_booking_value: Average revenue per booking
    
    Raises:
        ValueError: If date format is invalid
    
    Example:
        >>> report = generate_revenue_report('2024-01-01', '2024-01-31')
        >>> report['total_revenue']
        1250.50
    """
    date_filtered = bool(start_date or end_date)

    # Parse dates only when the caller requests a date range. The dashboard
    # needs total active reservation value, including future check-ins.
    if start_date:
        start_date = datetime.strptime(start_date, DATE_FORMAT)
    if end_date:
        end_date = datetime.strptime(end_date, DATE_FORMAT)
    if date_filtered and not start_date:
        start_date = datetime.min
    if date_filtered and not end_date:
        end_date = datetime.max

    if date_filtered and start_date > end_date:
        start_date, end_date = end_date, start_date
    
    total_revenue: float = 0.0
    payment_methods: Dict[str, float] = {}
    bookings_in_range: int = 0

    for booking in bookings.values():
        if booking.get('status') == 'CANCELLED':
            continue
        
        try:
            booking_date = datetime.strptime(booking['check_in'], DATE_FORMAT)
        except ValueError:
            continue
        
        if not date_filtered or start_date.date() <= booking_date.date() <= end_date.date():
            total_revenue += booking.get('total_amount', 0)
            bookings_in_range += 1

            payment = payments.get(booking.get('payment_id'))
            method = payment.get('payment_method', 'Unpaid') if payment else 'Unpaid'
            payment_methods[method] = payment_methods.get(method, 0.0) + booking.get('total_amount', 0)
    
    # Round values to 2 decimal places
    total_revenue = round(total_revenue, 2)
    payment_methods = {k: round(v, 2) for k, v in payment_methods.items()}
    avg_booking = round(total_revenue / bookings_in_range, 2) if bookings_in_range > 0 else 0.0
    
    return {
        'start_date': start_date.strftime(DATE_FORMAT) if date_filtered else None,
        'end_date': end_date.strftime(DATE_FORMAT) if date_filtered else None,
        'total_revenue': total_revenue,
        'bookings_count': bookings_in_range,
        'payment_methods': payment_methods,
        'average_booking_value': avg_booking,
        'generated_at': local_now().strftime(DATETIME_FORMAT)
    }


def generate_guest_report() -> Dict[str, Any]:
    """
    Generate guest report showing guest statistics and top guests.
    
    Returns:
        Dict[str, Any]: Report containing:
            - total_guests: Total number of guests
            - guests_with_bookings: Number of guests with at least one booking
            - top_guests: Top 5 guests by booking count
    
    Example:
        >>> report = generate_guest_report()
        >>> report['total_guests']
        10
        >>> report['top_guests'][0]['name']
        'John Doe'
    """
    total_guests = len(guests)
    guests_with_bookings = 0
    booking_counts: Dict[int, int] = {}
    
    for guest_id, guest in guests.items():
        booking_count = len(guest['bookings'])
        booking_counts[guest_id] = booking_count
        
        if booking_count > 0:
            guests_with_bookings += 1
        
    
    # Top guests by booking count
    sorted_guests = sorted(booking_counts.items(), key=lambda x: x[1], reverse=True)
    top_guests: List[Dict[str, Any]] = []
    
    for guest_id, count in sorted_guests[:5]:
        guest = guests[guest_id]
        top_guests.append({
            'guest_id': guest_id,
            'name': f"{guest['first_name']} {guest['last_name']}",
            'booking_count': count
        })
    
    return {
        'total_guests': total_guests,
        'guests_with_bookings': guests_with_bookings,
        'top_guests': top_guests,
        'generated_at': local_now().strftime(DATETIME_FORMAT)
    }


def generate_booking_report() -> Dict[str, Any]:
    """
    Generate booking report showing booking statistics.
    
    Returns:
        Dict[str, Any]: Report containing:
            - total_bookings: Total number of bookings
            - status_counts: Breakdown by status
            - upcoming_bookings: Up to 5 upcoming confirmed bookings
            - current_bookings: All current check-ins
    
    Example:
        >>> report = generate_booking_report()
        >>> report['total_bookings']
        15
        >>> report['status_counts']['CONFIRMED']
        5
    """
    total_bookings = len(bookings)
    status_counts: Dict[str, int] = {
        'CONFIRMED': 0,
        'CHECKED_IN': 0,
        'CHECKED_OUT': 0,
        'CANCELLED': 0
    }
    
    upcoming_bookings: List[Dict[str, Any]] = []
    current_bookings: List[Dict[str, Any]] = []
    today = local_now().date()
    
    for booking_id, booking in bookings.items():
        status = booking['status']
        status_counts[status] = status_counts.get(status, 0) + 1
        
        check_in = datetime.strptime(booking['check_in'], DATE_FORMAT).date()
        check_out = datetime.strptime(booking['check_out'], DATE_FORMAT).date()
        
        # Upcoming confirmed bookings
        if status == 'CONFIRMED' and check_in >= today:
            guest = get_guest(booking['guest_id'])
            upcoming_bookings.append({
                'booking_id': booking_id,
                'guest_name': f"{guest['first_name']} {guest['last_name']}",
                'room_number': booking['room_number'],
                'check_in': booking['check_in'],
                'check_out': booking['check_out']
            })
        
        # Current check-ins
        if status == 'CHECKED_IN':
            guest = get_guest(booking['guest_id'])
            current_bookings.append({
                'booking_id': booking_id,
                'guest_name': f"{guest['first_name']} {guest['last_name']}",
                'room_number': booking['room_number'],
                'check_out': booking['check_out']
            })
    
    # Sort upcoming bookings by check-in date
    upcoming_bookings.sort(key=lambda x: x['check_in'])
    
    return {
        'total_bookings': total_bookings,
        'status_counts': status_counts,
        'upcoming_bookings': upcoming_bookings[:5],
        'current_bookings': current_bookings,
        'generated_at': local_now().strftime(DATETIME_FORMAT)
    }


def generate_full_report() -> Dict[str, Any]:
    """
    Generate a full system report combining all report types.
    
    Returns:
        Dict[str, Any]: Complete report containing:
            - occupancy: Occupancy report
            - revenue: Revenue report
            - guests: Guest report
            - bookings: Booking report
            - generated_at: Report generation timestamp
    
    Example:
        >>> report = generate_full_report()
        >>> report['occupancy']['occupancy_rate']
        37.5
        >>> report['generated_at']
        '2024-01-01 12:00:00'
    """
    return {
        'occupancy': generate_occupancy_report(),
        'revenue': generate_revenue_report(),
        'guests': generate_guest_report(),
        'bookings': generate_booking_report(),
        'generated_at': local_now().strftime(DATETIME_FORMAT)
    }


# ============================================
# FIXED: Additional report helper functions
# ============================================

def generate_daily_revenue_report(date: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate revenue report for a specific day.
    
    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
    
    Returns:
        Dict[str, Any]: Daily revenue report
    
    Example:
        >>> report = generate_daily_revenue_report('2024-01-01')
        >>> report['total_revenue']
        125.50
    """
    if date is None:
        date = local_now().strftime(DATE_FORMAT)
    
    start_date = f"{date} 00:00:00"
    end_date = f"{date} 23:59:59"
    
    return generate_revenue_report(start_date, end_date)


def generate_monthly_revenue_report(year: int, month: int) -> Dict[str, Any]:
    """
    Generate revenue report for a specific month.
    
    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
    
    Returns:
        Dict[str, Any]: Monthly revenue report
    
    Example:
        >>> report = generate_monthly_revenue_report(2024, 1)
        >>> report['total_revenue']
        1250.50
    """
    start_date = datetime(year, month, 1).strftime(DATE_FORMAT)
    
    # Calculate last day of month
    if month == 12:
        end_date = datetime(year, month, 31).strftime(DATE_FORMAT)
    else:
        next_month = datetime(year, month + 1, 1)
        end_date = (next_month - timedelta(days=1)).strftime(DATE_FORMAT)
    
    return generate_revenue_report(start_date, end_date)


def generate_yearly_revenue_report(year: int) -> Dict[str, Any]:
    """
    Generate revenue report for a specific year.
    
    Args:
        year: Year (e.g., 2024)
    
    Returns:
        Dict[str, Any]: Yearly revenue report
    
    Example:
        >>> report = generate_yearly_revenue_report(2024)
        >>> report['total_revenue']
        15000.00
    """
    start_date = datetime(year, 1, 1).strftime(DATE_FORMAT)
    end_date = datetime(year, 12, 31).strftime(DATE_FORMAT)
    
    return generate_revenue_report(start_date, end_date)


def generate_room_utilization_report() -> Dict[str, Any]:
    """
    Generate room utilization report showing how often rooms are booked.
    
    Returns:
        Dict[str, Any]: Room utilization report
    
    Example:
        >>> report = generate_room_utilization_report()
        >>> report['most_booked_room']
        101
    """
    room_booking_counts: Dict[int, int] = {}
    
    for room_id, room in rooms.items():
        room_booking_counts[room_id] = len(room['bookings'])
    
    # Sort rooms by booking count
    sorted_rooms = sorted(room_booking_counts.items(), key=lambda x: x[1], reverse=True)
    
    top_rooms = []
    for room_id, count in sorted_rooms[:5]:
        room = rooms[room_id]
        top_rooms.append({
            'room_id': room_id,
            'room_number': room['room_number'],
            'room_type': room['room_type'],
            'booking_count': count
        })
    
    total_bookings = sum(room_booking_counts.values())
    avg_bookings = round(total_bookings / len(rooms), 2) if len(rooms) > 0 else 0
    
    return {
        'total_rooms': len(rooms),
        'total_bookings': total_bookings,
        'average_bookings_per_room': avg_bookings,
        'most_booked_rooms': top_rooms,
        'generated_at': local_now().strftime(DATETIME_FORMAT)
    }


