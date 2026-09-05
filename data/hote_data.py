"""
Data storage module using global dictionaries
"""

import json
import os
import shutil
import logging
from datetime import datetime
from config import DATA_FILE_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global data structures
guests = {}
rooms = {}
bookings = {}
payments = {}

# ID counters
guest_id_counter = 1
room_id_counter = 1
booking_id_counter = 1
payment_id_counter = 1

# File paths
DATA_FILE_PATH = 'hotel_data.json'
BACKUP_FILE_PATH = 'hotel_data.json.backup'


def initialize_data():
    """Initialize with sample rooms, guests, bookings, and payments"""
    global rooms, room_id_counter, guests, guest_id_counter, bookings, booking_id_counter, payments, payment_id_counter
    
    logger.info("Initializing default data...")
    
    # ============================================
    # SAMPLE ROOMS
    # ============================================
    sample_rooms = [
        # Floor 1 - Standard Rooms
        {'room_number': 101, 'room_type': 'STANDARD', 'floor': 1, 'status': 'AVAILABLE'},
        {'room_number': 102, 'room_type': 'STANDARD', 'floor': 1, 'status': 'AVAILABLE'},
        {'room_number': 103, 'room_type': 'STANDARD', 'floor': 1, 'status': 'AVAILABLE'},
        {'room_number': 104, 'room_type': 'STANDARD', 'floor': 1, 'status': 'AVAILABLE'},
        
        # Floor 1 - Deluxe Rooms
        {'room_number': 105, 'room_type': 'DELUXE', 'floor': 1, 'status': 'AVAILABLE'},
        {'room_number': 106, 'room_type': 'DELUXE', 'floor': 1, 'status': 'AVAILABLE'},
        
        # Floor 2 - Standard Rooms
        {'room_number': 201, 'room_type': 'STANDARD', 'floor': 2, 'status': 'AVAILABLE'},
        {'room_number': 202, 'room_type': 'STANDARD', 'floor': 2, 'status': 'AVAILABLE'},
        {'room_number': 203, 'room_type': 'STANDARD', 'floor': 2, 'status': 'AVAILABLE'},
        {'room_number': 204, 'room_type': 'STANDARD', 'floor': 2, 'status': 'AVAILABLE'},
        
        # Floor 2 - Deluxe Rooms
        {'room_number': 205, 'room_type': 'DELUXE', 'floor': 2, 'status': 'AVAILABLE'},
        {'room_number': 206, 'room_type': 'DELUXE', 'floor': 2, 'status': 'AVAILABLE'},
        
        # Floor 3 - Suite Rooms
        {'room_number': 301, 'room_type': 'SUITE', 'floor': 3, 'status': 'AVAILABLE'},
        {'room_number': 302, 'room_type': 'SUITE', 'floor': 3, 'status': 'AVAILABLE'},
        {'room_number': 303, 'room_type': 'SUITE', 'floor': 3, 'status': 'AVAILABLE'},
        
        # Floor 3 - Penthouse
        {'room_number': 304, 'room_type': 'PENTHOUSE', 'floor': 3, 'status': 'AVAILABLE'},
        
        # Floor 4 - Penthouse
        {'room_number': 401, 'room_type': 'PENTHOUSE', 'floor': 4, 'status': 'AVAILABLE'},
        {'room_number': 402, 'room_type': 'PENTHOUSE', 'floor': 4, 'status': 'AVAILABLE'},
        
        # Some rooms with different statuses for testing
        {'room_number': 107, 'room_type': 'DELUXE', 'floor': 1, 'status': 'MAINTENANCE'},
        {'room_number': 207, 'room_type': 'DELUXE', 'floor': 2, 'status': 'CLEANING'},
    ]
    
    for room_data in sample_rooms:
        room_id = room_id_counter
        room_data['room_id'] = room_id
        room_data['bookings'] = []
        room_data['current_booking'] = None
        rooms[room_id] = room_data
        room_id_counter += 1
    
    logger.info(f"✅ Created {len(sample_rooms)} sample rooms")
    
    # ============================================
    # SAMPLE GUESTS
    # ============================================
    sample_guests = [
        {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@email.com',
            'phone': '09171234567',
            'address': '123 Main St, Manila',
            'bookings': []
        },
        {
            'first_name': 'Maria',
            'last_name': 'Santos',
            'email': 'maria.santos@email.com',
            'phone': '09181234567',
            'address': '456 Oak Ave, Quezon City',
            'bookings': []
        },
        {
            'first_name': 'David',
            'last_name': 'Chen',
            'email': 'david.chen@email.com',
            'phone': '09191234567',
            'address': '789 Pine St, Makati',
            'bookings': []
        },
        {
            'first_name': 'Anna',
            'last_name': 'Reyes',
            'email': 'anna.reyes@email.com',
            'phone': '09201234567',
            'address': '321 Cedar Rd, Pasig',
            'bookings': []
        },
        {
            'first_name': 'Michael',
            'last_name': 'Tan',
            'email': 'michael.tan@email.com',
            'phone': '09211234567',
            'address': '654 Birch Ln, BGC',
            'bookings': []
        },
        {
            'first_name': 'Sarah',
            'last_name': 'Lim',
            'email': 'sarah.lim@email.com',
            'phone': '09221234567',
            'address': '987 Maple Dr, Alabang',
            'bookings': []
        },
        {
            'first_name': 'Robert',
            'last_name': 'Garcia',
            'email': 'robert.garcia@email.com',
            'phone': '09231234567',
            'address': '147 Willow St, Mandaluyong',
            'bookings': []
        },
        {
            'first_name': 'Lisa',
            'last_name': 'Park',
            'email': 'lisa.park@email.com',
            'phone': '09241234567',
            'address': '258 Elm Ave, Pasay',
            'bookings': []
        }
    ]
    
    for guest_data in sample_guests:
        guest_id = guest_id_counter
        guest_data['guest_id'] = guest_id
        guests[guest_id] = guest_data
        guest_id_counter += 1
    
    logger.info(f"✅ Created {len(sample_guests)} sample guests")
    
    # ============================================
    # SAMPLE BOOKINGS
    # ============================================
    from datetime import datetime, timedelta
    today = datetime.now().date()
    
    sample_bookings = [
        # Past bookings (checked out)
        {
            'guest_id': 1,  # John Smith
            'room_id': 1,   # Room 101
            'check_in': (today - timedelta(days=10)).strftime('%Y-%m-%d'),
            'check_out': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
            'guest_count': 2,
            'special_requests': 'Extra pillows',
            'status': 'CHECKED_OUT',
            'total_amount': 1200.00,
            'payment_id': 1
        },
        {
            'guest_id': 2,  # Maria Santos
            'room_id': 5,   # Room 105
            'check_in': (today - timedelta(days=5)).strftime('%Y-%m-%d'),
            'check_out': (today - timedelta(days=2)).strftime('%Y-%m-%d'),
            'guest_count': 1,
            'special_requests': '',
            'status': 'CHECKED_OUT',
            'total_amount': 800.00,
            'payment_id': 2
        },
        # Active bookings (checked in)
        {
            'guest_id': 3,  # David Chen
            'room_id': 2,   # Room 102
            'check_in': (today - timedelta(days=2)).strftime('%Y-%m-%d'),
            'check_out': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            'guest_count': 2,
            'special_requests': 'Late check-out',
            'status': 'CHECKED_IN',
            'total_amount': 600.00,
            'payment_id': 3
        },
        {
            'guest_id': 4,  # Anna Reyes
            'room_id': 6,   # Room 106
            'check_in': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
            'check_out': (today + timedelta(days=4)).strftime('%Y-%m-%d'),
            'guest_count': 3,
            'special_requests': 'Extra bed',
            'status': 'CHECKED_IN',
            'total_amount': 1200.00,
            'payment_id': 4
        },
        # Future bookings (confirmed)
        {
            'guest_id': 5,  # Michael Tan
            'room_id': 13,  # Room 301
            'check_in': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'check_out': (today + timedelta(days=8)).strftime('%Y-%m-%d'),
            'guest_count': 4,
            'special_requests': 'Family suite, crib needed',
            'status': 'CONFIRMED',
            'total_amount': 1500.00,
            'payment_id': None
        },
        {
            'guest_id': 6,  # Sarah Lim
            'room_id': 9,   # Room 203
            'check_in': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
            'check_out': (today + timedelta(days=9)).strftime('%Y-%m-%d'),
            'guest_count': 2,
            'special_requests': '',
            'status': 'CONFIRMED',
            'total_amount': 500.00,
            'payment_id': None
        },
        # Cancelled booking
        {
            'guest_id': 7,  # Robert Garcia
            'room_id': 10,  # Room 204
            'check_in': (today - timedelta(days=3)).strftime('%Y-%m-%d'),
            'check_out': (today + timedelta(days=4)).strftime('%Y-%m-%d'),
            'guest_count': 2,
            'special_requests': '',
            'status': 'CANCELLED',
            'total_amount': 0.00,
            'payment_id': None
        }
    ]
    
    for booking_data in sample_bookings:
        booking_id = booking_id_counter
        booking_data['booking_id'] = booking_id
        booking_data['room_number'] = rooms[booking_data['room_id']]['room_number']
        booking_data['room_type'] = rooms[booking_data['room_id']]['room_type']
        booking_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate cost breakdown (simplified)
        from config import ROOM_TYPES, TAX_RATE, SERVICE_CHARGE_RATE
        check_in_date = datetime.strptime(booking_data['check_in'], '%Y-%m-%d')
        check_out_date = datetime.strptime(booking_data['check_out'], '%Y-%m-%d')
        nights = (check_out_date - check_in_date).days
        room_type = booking_data['room_type']
        room_price = ROOM_TYPES[room_type]['base_price']
        
        subtotal = room_price * nights
        tax = subtotal * TAX_RATE
        service_charge = subtotal * SERVICE_CHARGE_RATE
        total = subtotal + tax + service_charge
        
        booking_data['cost_breakdown'] = {
            'nights': nights,
            'room_price': room_price,
            'subtotal': subtotal,
            'tax': tax,
            'service_charge': service_charge,
            'total': total
        }
        
        if booking_data['status'] != 'CANCELLED':
            booking_data['total_amount'] = total
        
        bookings[booking_id] = booking_data
        
        # Update room status and bookings
        room = rooms[booking_data['room_id']]
        room['bookings'].append(booking_id)
        if booking_data['status'] == 'CHECKED_IN':
            room['current_booking'] = booking_id
            room['status'] = 'BOOKED'
        elif booking_data['status'] == 'CONFIRMED':
            room['status'] = 'BOOKED'
        
        # Update guest bookings
        guest = guests[booking_data['guest_id']]
        guest['bookings'].append(booking_id)
        
        booking_id_counter += 1
    
    logger.info(f"✅ Created {len(sample_bookings)} sample bookings")
    
    # ============================================
    # SAMPLE PAYMENTS
    # ============================================
    sample_payments = [
        {
            'booking_id': 1,
            'amount': 1200.00,
            'payment_method': 'Credit Card',
            'status': 'PAID',
            'transaction_date': (today - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'refund_date': None
        },
        {
            'booking_id': 2,
            'amount': 800.00,
            'payment_method': 'GCash',
            'status': 'PAID',
            'transaction_date': (today - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'refund_date': None
        },
        {
            'booking_id': 3,
            'amount': 600.00,
            'payment_method': 'Cash',
            'status': 'PAID',
            'transaction_date': (today - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'refund_date': None
        },
        {
            'booking_id': 4,
            'amount': 1200.00,
            'payment_method': 'Bank Transfer',
            'status': 'PAID',
            'transaction_date': (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'refund_date': None
        }
    ]
    
    for payment_data in sample_payments:
        payment_id = payment_id_counter
        payment_data['payment_id'] = payment_id
        payments[payment_id] = payment_data
        
        # Link payment to booking
        booking = bookings[payment_data['booking_id']]
        booking['payment_id'] = payment_id
        
        payment_id_counter += 1
    
    logger.info(f"✅ Created {len(sample_payments)} sample payments")
    
    # ============================================
    # SAVE AND LOG SUMMARY
    # ============================================
    save_data()
    
    logger.info("=" * 50)
    logger.info("📊 DATA INITIALIZATION COMPLETE!")
    logger.info(f"   🏠 Rooms: {len(rooms)}")
    logger.info(f"   👤 Guests: {len(guests)}")
    logger.info(f"   📅 Bookings: {len(bookings)}")
    logger.info(f"   💰 Payments: {len(payments)}")
    logger.info("=" * 50)
    
    return True


def save_data():
    """Save all data to a JSON file"""
    try:
        data = {
            'guests': guests,
            'rooms': rooms,
            'bookings': bookings,
            'payments': payments,
            'guest_id_counter': guest_id_counter,
            'room_id_counter': room_id_counter,
            'booking_id_counter': booking_id_counter,
            'payment_id_counter': payment_id_counter,
            'saved_at': datetime.now().isoformat()
        }
        
        # Write to temporary file first (atomic write)
        temp_file = DATA_FILE_PATH + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, default=str, ensure_ascii=False)
        
        # Create backup before overwriting
        if os.path.exists(DATA_FILE_PATH):
            shutil.copy2(DATA_FILE_PATH, BACKUP_FILE_PATH)
            logger.info(f"Backup created: {BACKUP_FILE_PATH}")
        
        # Replace with new file (atomic)
        os.replace(temp_file, DATA_FILE_PATH)
        
        logger.info(f"Data saved successfully to {DATA_FILE_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False


def load_data():
    """Load data from a JSON file"""
    global guests, rooms, bookings, payments
    global guest_id_counter, room_id_counter, booking_id_counter, payment_id_counter
    
    try:
        logger.info(f"Attempting to load data from {DATA_FILE_PATH}")
        
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Validate data structure
        required_keys = ['guests', 'rooms', 'bookings', 'payments', 
                        'guest_id_counter', 'room_id_counter', 
                        'booking_id_counter', 'payment_id_counter']
        
        for key in required_keys:
            if key not in data:
                logger.error(f"Missing required key in data: {key}")
                return load_from_backup()
        
        guests = data['guests']
        rooms = data['rooms']
        bookings = data['bookings']
        payments = data['payments']
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
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {DATA_FILE_PATH}: {e}")
        logger.info("Attempting to load from backup...")
        return load_from_backup()
        
    except Exception as e:
        logger.critical(f"Unexpected error loading data: {e}")
        logger.info("Attempting to load from backup...")
        return load_from_backup()


def load_from_backup():
    """Load data from backup file"""
    global guests, rooms, bookings, payments
    global guest_id_counter, room_id_counter, booking_id_counter, payment_id_counter
    
    try:
        if not os.path.exists(BACKUP_FILE_PATH):
            logger.warning(f"No backup found at {BACKUP_FILE_PATH}, initializing defaults")
            initialize_data()
            return True
        
        logger.info(f"Loading from backup: {BACKUP_FILE_PATH}")
        
        with open(BACKUP_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        required_keys = ['guests', 'rooms', 'bookings', 'payments', 
                        'guest_id_counter', 'room_id_counter', 
                        'booking_id_counter', 'payment_id_counter']
        
        for key in required_keys:
            if key not in data:
                logger.error("Backup data validation failed, initializing defaults")
                initialize_data()
                return True
        
        guests = data['guests']
        rooms = data['rooms']
        bookings = data['bookings']
        payments = data['payments']
        guest_id_counter = data['guest_id_counter']
        room_id_counter = data['room_id_counter']
        booking_id_counter = data['booking_id_counter']
        payment_id_counter = data['payment_id_counter']
        
        logger.info("Data loaded from backup successfully")
        return True
        
    except Exception as e:
        logger.critical(f"Failed to load from backup: {e}")
        logger.info("Initializing default data...")
        initialize_data()
        return True


def get_next_id(counter_type):
    """Get next available ID"""
    global guest_id_counter, room_id_counter, booking_id_counter, payment_id_counter
    
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