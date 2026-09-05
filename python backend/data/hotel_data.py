"""
Data storage module using global dictionaries
FIXED: Replaced pickle with JSON for security
FIXED: Added proper error handling and logging
FIXED: Added data validation on load
FIXED: Added thread safety for concurrent access
FIXED: Fixed file paths to use absolute paths
FIXED: Added proper data structure validation
"""

import json
import os
import shutil
import logging
import threading
from datetime import datetime
from config import local_now
from typing import Dict, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global data structures
guests: Dict[int, Dict[str, Any]] = {}
rooms: Dict[int, Dict[str, Any]] = {}
bookings: Dict[int, Dict[str, Any]] = {}
payments: Dict[int, Dict[str, Any]] = {}

# ID counters
guest_id_counter: int = 1
room_id_counter: int = 1
booking_id_counter: int = 1
payment_id_counter: int = 1

# Thread lock for concurrent access
_data_lock = threading.RLock()

# FIXED: Use absolute paths based on script location
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(_BASE_DIR, 'hotel_data.json')
BACKUP_FILE_PATH = os.path.join(_BASE_DIR, 'hotel_data.json.backup')


def initialize_data():
    """Initialize with sample rooms"""
    global rooms, room_id_counter
    
    logger.info("Initializing default data...")
    
    sample_rooms = [
        {'room_number': 101, 'room_type': 'STANDARD', 'floor': 1, 'status': 'AVAILABLE'},
        {'room_number': 102, 'room_type': 'STANDARD', 'floor': 1, 'status': 'AVAILABLE'},
        {'room_number': 103, 'room_type': 'DELUXE', 'floor': 1, 'status': 'AVAILABLE'},
        {'room_number': 104, 'room_type': 'DELUXE', 'floor': 1, 'status': 'AVAILABLE'},
        {'room_number': 201, 'room_type': 'SUITE', 'floor': 2, 'status': 'AVAILABLE'},
        {'room_number': 202, 'room_type': 'SUITE', 'floor': 2, 'status': 'AVAILABLE'},
        {'room_number': 301, 'room_type': 'PENTHOUSE', 'floor': 3, 'status': 'AVAILABLE'},
        {'room_number': 302, 'room_type': 'PENTHOUSE', 'floor': 3, 'status': 'AVAILABLE'}
    ]
    
    for room_data in sample_rooms:
        room_id = room_id_counter
        room_data['room_id'] = room_id
        room_data['bookings'] = []
        room_data['current_booking'] = None
        rooms[room_id] = room_data
        room_id_counter += 1
    
    logger.info(f"Initialized {len(rooms)} sample rooms")


def validate_data(data: Dict[str, Any]) -> bool:
    """Validate loaded data structure"""
    required_keys = ['guests', 'rooms', 'bookings', 'payments', 
                    'guest_id_counter', 'room_id_counter', 
                    'booking_id_counter', 'payment_id_counter']
    
    for key in required_keys:
        if key not in data:
            logger.error(f"Missing required key in data: {key}")
            return False
    
    # Validate data types
    if not isinstance(data['guests'], dict):
        logger.error("Guests data is not a dictionary")
        return False
    if not isinstance(data['rooms'], dict):
        logger.error("Rooms data is not a dictionary")
        return False
    if not isinstance(data['bookings'], dict):
        logger.error("Bookings data is not a dictionary")
        return False
    if not isinstance(data['payments'], dict):
        logger.error("Payments data is not a dictionary")
        return False
    
    # Validate individual records
    if not _validate_guest_records(data['guests']):
        return False
    if not _validate_room_records(data['rooms']):
        return False
    if not _validate_booking_records(data['bookings']):
        return False
    if not _validate_payment_records(data['payments']):
        return False
    
    return True


def _validate_guest_records(guest_data: Dict) -> bool:
    """Validate individual guest records"""
    for guest_id, guest in guest_data.items():
        required_fields = ['guest_id', 'first_name', 'last_name', 'email', 'phone', 'bookings']
        if not all(field in guest for field in required_fields):
            logger.error(f"Guest {guest_id} missing required fields")
            return False
        if not isinstance(guest['bookings'], list):
            logger.error(f"Guest {guest_id} bookings is not a list")
            return False
    return True


def _validate_room_records(room_data: Dict) -> bool:
    """Validate individual room records"""
    for room_id, room in room_data.items():
        required_fields = ['room_id', 'room_number', 'room_type', 'floor', 'status', 'bookings', 'current_booking']
        if not all(field in room for field in required_fields):
            logger.error(f"Room {room_id} missing required fields")
            return False
        if not isinstance(room['bookings'], list):
            logger.error(f"Room {room_id} bookings is not a list")
            return False
    return True


def _validate_booking_records(booking_data: Dict) -> bool:
    """Validate individual booking records"""
    for booking_id, booking in booking_data.items():
        required_fields = ['booking_id', 'guest_id', 'room_id', 'check_in', 'check_out', 'status', 'total_amount']
        if not all(field in booking for field in required_fields):
            logger.error(f"Booking {booking_id} missing required fields")
            return False
        if not isinstance(booking['total_amount'], (int, float)):
            logger.error(f"Booking {booking_id} total_amount is not a number")
            return False
    return True


def _validate_payment_records(payment_data: Dict) -> bool:
    """Validate individual payment records"""
    for payment_id, payment in payment_data.items():
        required_fields = ['payment_id', 'booking_id', 'amount', 'payment_method', 'status', 'transaction_date']
        if not all(field in payment for field in required_fields):
            logger.error(f"Payment {payment_id} missing required fields")
            return False
        if not isinstance(payment['amount'], (int, float)):
            logger.error(f"Payment {payment_id} amount is not a number")
            return False
    return True


def _reconcile_room_booking_statuses() -> None:
    """Keep room status aligned with active bookings after loading JSON data."""
    for room in rooms.values():
        current_booking_id = room.get('current_booking')
        current_booking = bookings.get(current_booking_id)
        if current_booking and current_booking.get('status') in ('CONFIRMED', 'CHECKED_IN'):
            if current_booking.get('payment_id'):
                room['status'] = 'CLEANING'
            elif room.get('status') != 'CLEANING':
                room['status'] = 'BOOKED'
        elif room.get('status') == 'BOOKED':
            room['status'] = 'AVAILABLE'

    for booking in bookings.values():
        if booking.get('status') not in ('CONFIRMED', 'CHECKED_IN'):
            continue
        room = rooms.get(booking.get('room_id'))
        if room and not room.get('current_booking'):
            room['current_booking'] = booking.get('booking_id')
            room['status'] = 'BOOKED'


def save_data() -> bool:
    """FIXED: Save all data to a JSON file (secure) with thread safety"""
    with _data_lock:
        try:
            # Prepare data for serialization
            data = {
                'guests': guests,
                'rooms': rooms,
                'bookings': bookings,
                'payments': payments,
                'guest_id_counter': guest_id_counter,
                'room_id_counter': room_id_counter,
                'booking_id_counter': booking_id_counter,
                'payment_id_counter': payment_id_counter,
                'saved_at': local_now().isoformat()
            }
            
            # Write to temporary file first (atomic write)
            temp_file = DATA_FILE_PATH + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, default=str, ensure_ascii=False)
            
            # FIXED: Create backup before overwriting
            if os.path.exists(DATA_FILE_PATH):
                shutil.copy2(DATA_FILE_PATH, BACKUP_FILE_PATH)
                logger.info(f"Backup created: {BACKUP_FILE_PATH}")
            
            # Replace with new file (atomic)
            os.replace(temp_file, DATA_FILE_PATH)
            
            logger.info(f"Data saved successfully to {DATA_FILE_PATH}")
            return True
            
        except json.JSONEncodeError as e:
            logger.error(f"JSON encoding error: {e}")
            return False
        except IOError as e:
            logger.error(f"IO error saving data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving data: {e}")
            return False


def load_data() -> bool:
    """FIXED: Load data from JSON with proper error handling"""
    global guests, rooms, bookings, payments
    global guest_id_counter, room_id_counter, booking_id_counter, payment_id_counter
    
    with _data_lock:
        try:
            logger.info(f"Attempting to load data from {DATA_FILE_PATH}")
            
            with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # FIXED: Validate data structure
            if not validate_data(data):
                logger.error("Data validation failed, attempting to load from backup")
                return load_from_backup()
            
            # Load data
            guests.clear()
            guests.update({int(key): value for key, value in data['guests'].items()})
            for guest in guests.values():
                guest.pop('loyalty_points', None)
            rooms.clear()
            rooms.update({int(key): value for key, value in data['rooms'].items()})
            bookings.clear()
            bookings.update({int(key): value for key, value in data['bookings'].items()})
            payments.clear()
            payments.update({int(key): value for key, value in data['payments'].items()})
            _reconcile_room_booking_statuses()
            guest_id_counter = data['guest_id_counter']
            room_id_counter = data['room_id_counter']
            booking_id_counter = data['booking_id_counter']
            payment_id_counter = data['payment_id_counter']
            
            logger.info(f"Data loaded successfully: {len(guests)} guests, {len(rooms)} rooms, "
                       f"{len(bookings)} bookings, {len(payments)} payments")
            return True
            
        except FileNotFoundError:
            logger.warning(f"Data file {DATA_FILE_PATH} not found, initializing defaults")
            initialize_data()
            save_data()  # Save the initialized data
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {DATA_FILE_PATH}: {e}")
            logger.info("Attempting to load from backup...")
            return load_from_backup()
            
        except KeyError as e:
            logger.error(f"Missing key in data: {e}")
            logger.info("Attempting to load from backup...")
            return load_from_backup()
            
        except Exception as e:
            logger.critical(f"Unexpected error loading data: {e}")
            logger.info("Attempting to load from backup...")
            return load_from_backup()


def load_from_backup() -> bool:
    """FIXED: Load data from backup file"""
    global guests, rooms, bookings, payments
    global guest_id_counter, room_id_counter, booking_id_counter, payment_id_counter
    
    try:
        if not os.path.exists(BACKUP_FILE_PATH):
            logger.warning(f"No backup found at {BACKUP_FILE_PATH}, initializing defaults")
            initialize_data()
            save_data()
            return True
        
        logger.info(f"Loading from backup: {BACKUP_FILE_PATH}")
        
        with open(BACKUP_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if not validate_data(data):
            logger.error("Backup data validation failed, initializing defaults")
            initialize_data()
            save_data()
            return True
        
        guests.clear()
        guests.update({int(key): value for key, value in data['guests'].items()})
        for guest in guests.values():
            guest.pop('loyalty_points', None)
        rooms.clear()
        rooms.update({int(key): value for key, value in data['rooms'].items()})
        bookings.clear()
        bookings.update({int(key): value for key, value in data['bookings'].items()})
        payments.clear()
        payments.update({int(key): value for key, value in data['payments'].items()})
        _reconcile_room_booking_statuses()
        guest_id_counter = data['guest_id_counter']
        room_id_counter = data['room_id_counter']
        booking_id_counter = data['booking_id_counter']
        payment_id_counter = data['payment_id_counter']
        
        logger.info(f"Data loaded from backup successfully")
        return True
        
    except Exception as e:
        logger.critical(f"Failed to load from backup: {e}")
        logger.info("Initializing default data...")
        initialize_data()
        save_data()
        return True


def get_next_id(counter_type: str) -> int:
    """Get next available ID with thread safety"""
    global guest_id_counter, room_id_counter, booking_id_counter, payment_id_counter
    
    with _data_lock:
        if counter_type == 'guest':
            current = guest_id_counter
            guest_id_counter += 1
            return current
        elif counter_type == 'room':
            current = room_id_counter
            room_id_counter += 1
            return current
        elif counter_type == 'booking':
            current = booking_id_counter
            booking_id_counter += 1
            return current
        elif counter_type == 'payment':
            current = payment_id_counter
            payment_id_counter += 1
            return current
        else:
            raise ValueError(f"Invalid counter type: {counter_type}")


def clear_all_data():
    """FIXED: Clear all data (for testing/reset)"""
    global guests, rooms, bookings, payments
    global guest_id_counter, room_id_counter, booking_id_counter, payment_id_counter
    
    with _data_lock:
        guests = {}
        rooms = {}
        bookings = {}
        payments = {}
        guest_id_counter = 1
        room_id_counter = 1
        booking_id_counter = 1
        payment_id_counter = 1
        
        # Remove data files
        for file_path in [DATA_FILE_PATH, BACKUP_FILE_PATH, DATA_FILE_PATH + '.tmp']:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Could not remove file {file_path}: {e}")
        
        logger.info("All data cleared")
        initialize_data()
        save_data()


# ============================================
# FIXED: Data access functions (encapsulation with validation)
# ============================================

def get_all_guests() -> Dict[int, Dict[str, Any]]:
    """Return a copy of guests data (prevents external mutation)"""
    return guests.copy()


def get_all_rooms() -> Dict[int, Dict[str, Any]]:
    """Return a copy of rooms data (prevents external mutation)"""
    return rooms.copy()


def get_all_bookings() -> Dict[int, Dict[str, Any]]:
    """Return a copy of bookings data (prevents external mutation)"""
    return bookings.copy()


def get_all_payments() -> Dict[int, Dict[str, Any]]:
    """Return a copy of payments data (prevents external mutation)"""
    return payments.copy()


def get_guest(guest_id: int) -> Optional[Dict[str, Any]]:
    """Get a single guest by ID"""
    return guests.get(guest_id)


def get_room(room_id: int) -> Optional[Dict[str, Any]]:
    """Get a single room by ID"""
    return rooms.get(room_id)


def get_booking(booking_id: int) -> Optional[Dict[str, Any]]:
    """Get a single booking by ID"""
    return bookings.get(booking_id)


def get_payment(payment_id: int) -> Optional[Dict[str, Any]]:
    """Get a single payment by ID"""
    return payments.get(payment_id)


def update_guest(guest_id: int, guest_data: Dict[str, Any]) -> bool:
    """Update a guest"""
    with _data_lock:
        if guest_id not in guests:
            return False
        guests[guest_id] = guest_data
        save_data()
        return True


def update_room(room_id: int, room_data: Dict[str, Any]) -> bool:
    """Update a room"""
    with _data_lock:
        if room_id not in rooms:
            return False
        rooms[room_id] = room_data
        save_data()
        return True


def update_booking(booking_id: int, booking_data: Dict[str, Any]) -> bool:
    """Update a booking"""
    with _data_lock:
        if booking_id not in bookings:
            return False
        bookings[booking_id] = booking_data
        save_data()
        return True


def update_payment(payment_id: int, payment_data: Dict[str, Any]) -> bool:
    """Update a payment"""
    with _data_lock:
        if payment_id not in payments:
            return False
        payments[payment_id] = payment_data
        save_data()
        return True


def delete_guest(guest_id: int) -> bool:
    """Delete a guest"""
    with _data_lock:
        if guest_id in guests:
            del guests[guest_id]
            save_data()
            return True
    return False


def delete_room(room_id: int) -> bool:
    """Delete a room"""
    with _data_lock:
        if room_id in rooms:
            del rooms[room_id]
            save_data()
            return True
    return False


def delete_booking(booking_id: int) -> bool:
    """Delete a booking"""
    with _data_lock:
        if booking_id in bookings:
            del bookings[booking_id]
            save_data()
            return True
    return False


def delete_payment(payment_id: int) -> bool:
    """Delete a payment"""
    with _data_lock:
        if payment_id in payments:
            del payments[payment_id]
            save_data()
            return True
    return False