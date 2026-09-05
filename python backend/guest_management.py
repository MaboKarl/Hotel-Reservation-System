"""
Guest Management Module - Procedural

This module handles all guest-related operations including:
- Creating, reading, updating, and deleting guests
- Searching for guests
- Managing guest bookings
"""

from typing import Dict, Any, Optional, List, Union
from data.hotel_data import guests, get_next_id, save_data, get_guest as db_get_guest
from utils.validators import validate_email, validate_phone, sanitize_input
from utils.error_handler import GuestError, ValidationError, NotFoundError, ConflictError


def create_guest(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    address: str = ""
) -> Dict[str, Any]:
    """
    Create a new guest.
    
    Args:
        first_name: Guest's first name
        last_name: Guest's last name
        email: Guest's email address (must be unique)
        phone: Guest's phone number (Philippine format)
        address: Guest's address (optional)
    
    Returns:
        Dict[str, Any]: Guest data dictionary
    
    Raises:
        ValidationError: If input validation fails
        ConflictError: If email already exists
    
    Example:
        >>> guest = create_guest('John', 'Doe', 'john@example.com', '09171234567')
        >>> guest['first_name']
        'John'
    """
    # Sanitize inputs
    first_name = sanitize_input(first_name)
    last_name = sanitize_input(last_name)
    email = sanitize_input(email)
    phone = sanitize_input(phone)
    address = sanitize_input(address)
    
    # Validate required fields
    if not first_name or not last_name:
        raise ValidationError("First name and last name are required")
    
    # Validate email
    if not validate_email(email):
        raise ValidationError(f"Invalid email format: {email}")
    
    # Validate phone
    if not validate_phone(phone):
        raise ValidationError(f"Invalid phone number: {phone}")
    
    # Check duplicate email
    for guest_id, guest in guests.items():
        if guest['email'].lower() == email.lower():
            raise ConflictError(f"Guest with email {email} already exists", field="email")
    
    # Create guest
    guest_id = get_next_id('guest')
    guest_data: Dict[str, Any] = {
        'guest_id': guest_id,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': phone,
        'address': address,
        'bookings': []
    }
    
    guests[guest_id] = guest_data
    save_data()
    return guest_data


def get_guest(guest_id: Union[int, str]) -> Dict[str, Any]:
    """
    Get guest by ID.
    
    Args:
        guest_id: Guest ID (int or string that can be converted to int)
    
    Returns:
        Dict[str, Any]: Guest data dictionary
    
    Raises:
        ValidationError: If guest_id format is invalid
        NotFoundError: If guest not found
    
    Example:
        >>> guest = get_guest(1)
        >>> guest['first_name']
        'John'
    """
    try:
        guest_id = int(guest_id)
    except (ValueError, TypeError):
        raise ValidationError("Invalid guest ID format")
    
    guest = guests.get(guest_id)
    if not guest:
        raise NotFoundError("Guest", guest_id)
    return guest


def update_guest(guest_id: Union[int, str], **kwargs) -> Dict[str, Any]:
    """
    Update guest information.
    
    Args:
        guest_id: Guest ID to update
        **kwargs: Fields to update (first_name, last_name, email, phone, address)
    
    Returns:
        Dict[str, Any]: Updated guest data
    
    Raises:
        ValidationError: If input validation fails
        NotFoundError: If guest not found
        ConflictError: If email already exists
    
    Example:
        >>> guest = update_guest(1, first_name='Jane', phone='09171234568')
        >>> guest['first_name']
        'Jane'
    """
    guest = get_guest(guest_id)
    
    allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'address']
    
    for key, value in kwargs.items():
        if key not in allowed_fields:
            continue
            
        if not value:
            continue
            
        if key == 'email':
            # Validate email format
            if not validate_email(value):
                raise ValidationError(f"Invalid email format: {value}", field="email")
            
            # Check duplicate email
            for g_id, g in guests.items():
                if g_id != guest_id and g['email'].lower() == value.lower():
                    raise ConflictError(f"Guest with email {value} already exists", field="email")
            
            guest['email'] = value
            
        elif key == 'phone':
            # Validate phone number
            if not validate_phone(value):
                raise ValidationError(f"Invalid phone number: {value}", field="phone")
            guest['phone'] = value
            
        elif key in ['first_name', 'last_name']:
            # Sanitize and validate name
            value = sanitize_input(value)
            if not value:
                raise ValidationError(f"{key.replace('_', ' ').title()} is required", field=key)
            guest[key] = value
            
        elif key == 'address':
            guest['address'] = sanitize_input(value)
    
    # Save updated guest
    guests[guest_id] = guest
    save_data()
    return guest


def delete_guest(guest_id: Union[int, str]) -> bool:
    """
    Delete a guest.
    
    Args:
        guest_id: Guest ID to delete
    
    Returns:
        bool: True if deleted successfully
    
    Raises:
        NotFoundError: If guest not found
        GuestError: If guest has active bookings
    
    Example:
        >>> delete_guest(1)
        True
    """
    guest = get_guest(guest_id)
    
    # Check for active bookings
    if guest['bookings']:
        from booking_management import get_booking
        active_bookings: List[int] = []
        
        for booking_id in guest['bookings']:
            booking = get_booking(booking_id)
            if booking['status'] not in ['CHECKED_OUT', 'CANCELLED']:
                active_bookings.append(booking_id)
        
        if active_bookings:
            raise GuestError(
                f"Cannot delete guest with active bookings: {active_bookings}",
                details={'active_bookings': active_bookings}
            )
    
    # Delete guest
    del guests[guest_id]
    save_data()
    return True


def list_guests() -> Dict[int, Dict[str, Any]]:
    """
    List all guests.
    
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary of all guests
    
    Example:
        >>> guests = list_guests()
        >>> len(guests)
        5
    """
    return guests.copy()


def search_guests(search_term: Optional[str]) -> Dict[int, Dict[str, Any]]:
    """
    Search guests by first name, last name, email, or phone.
    
    Args:
        search_term: Search term (case-insensitive)
    
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary of matching guests
    
    Example:
        >>> results = search_guests('John')
        >>> for guest in results.values():
        ...     print(guest['first_name'])
        John
        Johnny
    """
    if not search_term:
        return list_guests()
    
    search_term = search_term.lower().strip()
    results: Dict[int, Dict[str, Any]] = {}
    
    for guest_id, guest in guests.items():
        if (search_term in guest['first_name'].lower() or
            search_term in guest['last_name'].lower() or
            search_term in guest['email'].lower() or
            search_term in guest['phone']):
            results[guest_id] = guest
    
    return results


def add_booking_to_guest(guest_id: Union[int, str], booking_id: int) -> bool:
    """
    Add a booking reference to a guest.
    
    Args:
        guest_id: Guest ID
        booking_id: Booking ID to add
    
    Returns:
        bool: True if booking was added successfully
    
    Raises:
        NotFoundError: If guest not found
    
    Example:
        >>> add_booking_to_guest(1, 101)
        True
    """
    guest = get_guest(guest_id)
    if booking_id not in guest['bookings']:
        guest['bookings'].append(booking_id)
        guests[guest_id] = guest
        save_data()
    return True


def get_guest_bookings_count(guest_id: Union[int, str]) -> int:
    """
    Get the number of bookings for a guest.
    
    Args:
        guest_id: Guest ID
    
    Returns:
        int: Number of bookings
    
    Raises:
        NotFoundError: If guest not found
    
    Example:
        >>> get_guest_bookings_count(1)
        3
    """
    guest = get_guest(guest_id)
    return len(guest['bookings'])


def get_guest_full_name(guest_id: Union[int, str]) -> str:
    """
    Get the full name of a guest.
    
    Args:
        guest_id: Guest ID
    
    Returns:
        str: Full name (first_name + last_name)
    
    Raises:
        NotFoundError: If guest not found
    
    Example:
        >>> get_guest_full_name(1)
        'John Doe'
    """
    guest = get_guest(guest_id)
    return f"{guest['first_name']} {guest['last_name']}"


def guest_exists(guest_id: Union[int, str]) -> bool:
    """
    Check if a guest exists.
    
    Args:
        guest_id: Guest ID to check
    
    Returns:
        bool: True if guest exists, False otherwise
    
    Example:
        >>> guest_exists(1)
        True
        >>> guest_exists(999)
        False
    """
    try:
        guest_id = int(guest_id)
        return guest_id in guests
    except (ValueError, TypeError):
        return False


def get_guests_with_bookings() -> Dict[int, Dict[str, Any]]:
    """
    Get all guests that have at least one booking.
    
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary of guests with bookings
    
    Example:
        >>> guests_with_bookings = get_guests_with_bookings()
        >>> len(guests_with_bookings)
        3
    """
    result: Dict[int, Dict[str, Any]] = {}
    for guest_id, guest in guests.items():
        if guest['bookings']:
            result[guest_id] = guest
    return result


