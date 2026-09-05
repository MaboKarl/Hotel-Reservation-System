"""
Configuration constants for the Hotel Management System
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Final
from zoneinfo import ZoneInfo

TIME_ZONE: Final[str] = 'Asia/Manila'
try:
    LOCAL_TIME_ZONE = ZoneInfo(TIME_ZONE)
except Exception:
    # Windows installations may not include the IANA timezone database.
    LOCAL_TIME_ZONE = timezone(timedelta(hours=8), name='PHT')

# Room types and their base prices
ROOM_TYPES: Final[Dict[str, Dict[str, float | int]]] = {
    'STANDARD': {'capacity': 2, 'base_price': 4500.00},
    'DELUXE': {'capacity': 4, 'base_price': 7000.00},
    'SUITE': {'capacity': 6, 'base_price': 12000.00},
    'PENTHOUSE': {'capacity': 8, 'base_price': 20000.00}
}

# Room statuses
ROOM_STATUSES: Final[Dict[str, str]] = {
    'AVAILABLE': 'Available',
    'BOOKED': 'Booked',
    'MAINTENANCE': 'Under Maintenance',
    'CLEANING': 'Being Cleaned'
}

# Payment statuses
PAYMENT_STATUSES: Final[Dict[str, str]] = {
    'PENDING': 'Pending',
    'PAID': 'Paid',
    'CANCELLED': 'Cancelled',
    'REFUNDED': 'Refunded'
}

# Booking statuses
BOOKING_STATUSES: Final[Dict[str, str]] = {
    'CONFIRMED': 'Confirmed',
    'CHECKED_IN': 'Checked In',
    'CHECKED_OUT': 'Checked Out',
    'CANCELLED': 'Cancelled'
}

# Tax and service charges
TAX_RATE: Final[float] = 0.12  # 12% tax
SERVICE_CHARGE_RATE: Final[float] = 0.05  # 5% service charge

# Validation constants
MAX_GUESTS_PER_ROOM: Final[int] = 8
MIN_STAY_DAYS: Final[int] = 1
MAX_STAY_DAYS: Final[int] = 30

# File paths for data persistence
DATA_FILE_PATH: Final[str] = 'hotel_data.json'


# ============================================
# FIXED #15: Date format constants
# ============================================

DATE_FORMAT: Final[str] = '%Y-%m-%d'
DATETIME_FORMAT: Final[str] = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT: Final[str] = '%H:%M:%S'


# ============================================
# Date helper functions
# ============================================

def get_date_format() -> str:
    """Get the standard date format."""
    return DATE_FORMAT


def get_datetime_format() -> str:
    """Get the standard datetime format."""
    return DATETIME_FORMAT


def get_time_format() -> str:
    """Get the standard time format."""
    return TIME_FORMAT


def format_date(date_obj) -> str:
    """Format a date object using the standard format."""
    return date_obj.strftime(DATE_FORMAT)


def format_datetime(datetime_obj) -> str:
    """Format a datetime object using the standard format."""
    return datetime_obj.strftime(DATETIME_FORMAT)


def parse_date(date_str: str):
    """Parse a date string using the standard format."""
    from datetime import datetime
    return datetime.strptime(date_str, DATE_FORMAT)


def parse_datetime(datetime_str: str):
    """Parse a datetime string using the standard format."""
    from datetime import datetime
    return datetime.strptime(datetime_str, DATETIME_FORMAT)


def local_now() -> datetime:
    """Return current hotel time as a timezone-adjusted naive datetime."""
    return datetime.now(LOCAL_TIME_ZONE).replace(tzinfo=None)