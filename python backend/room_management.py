"""
Room Management Module - Procedural

This module handles all room-related operations including:
- Creating, reading, updating, and deleting rooms
- Managing room availability and status
- Tracking room bookings
"""

from typing import Dict, Any, Optional, List, Union
from data.hotel_data import rooms, get_next_id, save_data
from utils.validators import validate_room_type
from utils.error_handler import RoomError, ValidationError, NotFoundError, ConflictError


# Valid room statuses
VALID_STATUSES: List[str] = ['AVAILABLE', 'BOOKED', 'MAINTENANCE', 'CLEANING']


def create_room(
    room_number: Union[int, str],
    room_type: str,
    floor: Union[int, str],
    image_url: str = '',
    details: str = '',
    name: str = ''
) -> Dict[str, Any]:
    """
    Create a new room.
    
    Args:
        room_number: Room number (must be unique and positive)
        room_type: Room type (STANDARD, DELUXE, SUITE, PENTHOUSE)
        floor: Floor number (must be positive)
    
    Returns:
        Dict[str, Any]: Room data dictionary
    
    Raises:
        ValidationError: If input validation fails
        ConflictError: If room number already exists
    
    Example:
        >>> room = create_room(101, 'STANDARD', 1)
        >>> room['room_number']
        101
    """
    try:
        room_number = int(room_number)
        floor = int(floor)
    except (ValueError, TypeError):
        raise ValidationError("Room number and floor must be integers")
    
    if not validate_room_type(room_type):
        raise ValidationError(f"Invalid room type: {room_type}")
    
    if room_number <= 0:
        raise ValidationError("Room number must be positive", field="room_number")
    
    if floor <= 0:
        raise ValidationError("Floor must be positive", field="floor")
    
    # Check duplicate room number
    for room_id, room in rooms.items():
        if room['room_number'] == room_number:
            raise ConflictError(f"Room {room_number} already exists", field="room_number")
    
    room_id = get_next_id('room')
    room_data: Dict[str, Any] = {
        'room_id': room_id,
        'room_number': room_number,
        'room_type': room_type.upper(),
        'floor': floor,
        'status': 'AVAILABLE',
        'current_booking': None,
        'bookings': [],
        'image_url': image_url,
        'details': details,
        'name': name
    }
    
    rooms[room_id] = room_data
    save_data()
    return room_data


def get_room(room_id: Union[int, str]) -> Dict[str, Any]:
    """
    Get room by ID.
    
    Args:
        room_id: Room ID (int or string that can be converted to int)
    
    Returns:
        Dict[str, Any]: Room data dictionary
    
    Raises:
        ValidationError: If room_id format is invalid
        NotFoundError: If room not found
    
    Example:
        >>> room = get_room(1)
        >>> room['room_number']
        101
    """
    try:
        room_id = int(room_id)
    except (ValueError, TypeError):
        raise ValidationError("Invalid room ID format")
    
    room = rooms.get(room_id)
    if not room:
        raise NotFoundError("Room", room_id)
    return room


def get_room_by_number(room_number: int) -> Dict[str, Any]:
    """
    Get room by room number.
    
    Args:
        room_number: Room number to search for
    
    Returns:
        Dict[str, Any]: Room data dictionary
    
    Raises:
        NotFoundError: If room not found
    
    Example:
        >>> room = get_room_by_number(101)
        >>> room['room_id']
        1
    """
    for room_id, room in rooms.items():
        if room['room_number'] == room_number:
            return room
    raise NotFoundError("Room", room_number)


def update_room(room_id: Union[int, str], **kwargs) -> Dict[str, Any]:
    """
    Update room information.
    
    Args:
        room_id: Room ID to update
        **kwargs: Fields to update (room_type, status)
    
    Returns:
        Dict[str, Any]: Updated room data
    
    Raises:
        ValidationError: If input validation fails
        NotFoundError: If room not found
    
    Example:
        >>> room = update_room(1, status='MAINTENANCE')
        >>> room['status']
        'MAINTENANCE'
    """
    room = get_room(room_id)
    
    allowed_fields = ['room_type', 'status', 'image_url', 'details', 'name']
    
    for key, value in kwargs.items():
        if key not in allowed_fields:
            continue
            
        if not value:
            continue
            
        if key == 'room_type':
            if not validate_room_type(value):
                raise ValidationError(f"Invalid room type: {value}", field="room_type")
            room['room_type'] = value.upper()
            
        elif key == 'status':
            if value not in VALID_STATUSES:
                raise ValidationError(f"Invalid status: {value}", field="status")
            room['status'] = value

        elif key == 'image_url':
            room['image_url'] = str(value).strip()
        elif key == 'details':
            room['details'] = str(value).strip()
        elif key == 'name':
            room['name'] = str(value).strip()
    
    rooms[room_id] = room
    save_data()
    return room


def update_room_status(room_id: Union[int, str], status: str) -> Dict[str, Any]:
    """
    Update room status.
    
    Args:
        room_id: Room ID to update
        status: New status (AVAILABLE, BOOKED, MAINTENANCE, CLEANING)
    
    Returns:
        Dict[str, Any]: Updated room data
    
    Raises:
        ValidationError: If status is invalid
        NotFoundError: If room not found
    
    Example:
        >>> room = update_room_status(1, 'CLEANING')
        >>> room['status']
        'CLEANING'
    """
    if status not in VALID_STATUSES:
        raise ValidationError(f"Invalid status: {status}", field="status")
    
    room = get_room(room_id)
    room['status'] = status
    rooms[room_id] = room
    save_data()
    return room


def delete_room(room_id: Union[int, str]) -> bool:
    """
    Delete a room.
    
    Args:
        room_id: Room ID to delete
    
    Returns:
        bool: True if deleted successfully
    
    Raises:
        NotFoundError: If room not found
        RoomError: If room is booked or has booking history
    
    Example:
        >>> delete_room(1)
        True
    """
    room = get_room(room_id)
    
    if room['status'] == 'BOOKED':
        raise RoomError(
            "Cannot delete a room that is currently booked",
            details={'status': 'BOOKED', 'current_booking': room['current_booking']}
        )
    
    if room['bookings']:
        raise RoomError(
            "Cannot delete a room with booking history",
            details={'booking_count': len(room['bookings'])}
        )
    
    del rooms[room_id]
    save_data()
    return True


def list_rooms() -> Dict[int, Dict[str, Any]]:
    """
    List all rooms.
    
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary of all rooms
    
    Example:
        >>> rooms = list_rooms()
        >>> len(rooms)
        8
    """
    return rooms.copy()


def get_available_rooms(room_type: Optional[str] = None) -> Dict[int, Dict[str, Any]]:
    """
    Get all available rooms.
    
    Args:
        room_type: Optional room type filter (STANDARD, DELUXE, SUITE, PENTHOUSE)
    
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary of available rooms
    
    Example:
        >>> available = get_available_rooms('STANDARD')
        >>> for room in available.values():
        ...     print(room['room_number'])
        101
        102
    """
    available_rooms: Dict[int, Dict[str, Any]] = {}
    
    for room_id, room in rooms.items():
        if room['status'] == 'AVAILABLE':
            if room_type is None or room['room_type'] == room_type.upper():
                available_rooms[room_id] = room
    
    return available_rooms


def add_booking_to_room(room_id: Union[int, str], booking_id: int) -> bool:
    """
    Add a booking reference to a room.
    
    Args:
        room_id: Room ID
        booking_id: Booking ID to add
    
    Returns:
        bool: True if booking was added successfully
    
    Raises:
        NotFoundError: If room not found
    
    Example:
        >>> add_booking_to_room(1, 101)
        True
    """
    room = get_room(room_id)
    if booking_id not in room['bookings']:
        room['bookings'].append(booking_id)
        rooms[room_id] = room
        save_data()
    return True


def set_current_booking(room_id: Union[int, str], booking_id: int) -> bool:
    """
    Set the current booking for a room and update status to BOOKED.
    
    Args:
        room_id: Room ID
        booking_id: Booking ID to set as current
    
    Returns:
        bool: True if successful
    
    Raises:
        NotFoundError: If room not found
    
    Example:
        >>> set_current_booking(1, 101)
        True
    """
    room = get_room(room_id)
    room['current_booking'] = booking_id
    room['status'] = 'BOOKED'
    rooms[room_id] = room
    save_data()
    return True


def clear_current_booking(room_id: Union[int, str]) -> bool:
    """
    Clear the current booking from a room and update status to AVAILABLE.
    
    Args:
        room_id: Room ID
    
    Returns:
        bool: True if successful
    
    Raises:
        NotFoundError: If room not found
    
    Example:
        >>> clear_current_booking(1)
        True
    """
    room = get_room(room_id)
    room['current_booking'] = None
    room['status'] = 'AVAILABLE'
    rooms[room_id] = room
    save_data()
    return True


def get_room_by_status(status: str) -> Dict[int, Dict[str, Any]]:
    """
    Get all rooms with a specific status.
    
    Args:
        status: Room status (AVAILABLE, BOOKED, MAINTENANCE, CLEANING)
    
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary of rooms with the status
    
    Raises:
        ValidationError: If status is invalid
    
    Example:
        >>> booked_rooms = get_room_by_status('BOOKED')
        >>> len(booked_rooms)
        3
    """
    if status not in VALID_STATUSES:
        raise ValidationError(f"Invalid status: {status}", field="status")
    
    result: Dict[int, Dict[str, Any]] = {}
    for room_id, room in rooms.items():
        if room['status'] == status:
            result[room_id] = room
    return result


def get_rooms_by_type(room_type: str) -> Dict[int, Dict[str, Any]]:
    """
    Get all rooms of a specific type.
    
    Args:
        room_type: Room type (STANDARD, DELUXE, SUITE, PENTHOUSE)
    
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary of rooms with the type
    
    Raises:
        ValidationError: If room_type is invalid
    
    Example:
        >>> deluxe_rooms = get_rooms_by_type('DELUXE')
        >>> len(deluxe_rooms)
        2
    """
    if not validate_room_type(room_type):
        raise ValidationError(f"Invalid room type: {room_type}", field="room_type")
    
    result: Dict[int, Dict[str, Any]] = {}
    for room_id, room in rooms.items():
        if room['room_type'] == room_type.upper():
            result[room_id] = room
    return result


def get_room_count_by_status() -> Dict[str, int]:
    """
    Get counts of rooms by status.
    
    Returns:
        Dict[str, int]: Dictionary with status counts
    
    Example:
        >>> counts = get_room_count_by_status()
        >>> counts['AVAILABLE']
        5
    """
    counts: Dict[str, int] = {status: 0 for status in VALID_STATUSES}
    
    for room in rooms.values():
        status = room['status']
        if status in counts:
            counts[status] += 1
    
    return counts


def get_room_count_by_type() -> Dict[str, int]:
    """
    Get counts of rooms by type.
    
    Returns:
        Dict[str, int]: Dictionary with type counts
    
    Example:
        >>> counts = get_room_count_by_type()
        >>> counts['STANDARD']
        4
    """
    counts: Dict[str, int] = {}
    
    for room in rooms.values():
        room_type = room['room_type']
        counts[room_type] = counts.get(room_type, 0) + 1
    
    return counts


def is_room_available(room_id: Union[int, str]) -> bool:
    """
    Check if a room is available for booking.
    
    Args:
        room_id: Room ID to check
    
    Returns:
        bool: True if room is available, False otherwise
    
    Raises:
        NotFoundError: If room not found
    
    Example:
        >>> is_room_available(1)
        True
    """
    room = get_room(room_id)
    return room['status'] == 'AVAILABLE'


def get_current_booking(room_id: Union[int, str]) -> Optional[int]:
    """
    Get the current booking ID for a room.
    
    Args:
        room_id: Room ID
    
    Returns:
        Optional[int]: Booking ID if room has a current booking, None otherwise
    
    Raises:
        NotFoundError: If room not found
    
    Example:
        >>> get_current_booking(1)
        101
    """
    room = get_room(room_id)
    return room.get('current_booking')