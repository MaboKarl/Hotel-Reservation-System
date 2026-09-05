"""
Validation functions for the Hotel Management System
"""

import re
import html
from datetime import datetime
from config import local_now
from typing import Tuple, Optional, Union, Any


# ============================================
# Basic Validation Functions
# ============================================

def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number (Philippine format).
    
    Supports formats:
    - 09XXXXXXXXX (11 digits)
    - +639XXXXXXXXX (13 digits with +)
    - 639XXXXXXXXX (12 digits)
    """
    if not phone or not isinstance(phone, str):
        return False
    phone = re.sub(r'[\s\-\(\)]', '', str(phone))
    pattern = r'^(09|\+639|639)\d{9}$'
    return re.match(pattern, phone) is not None


def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    if not date_str or not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_dates(check_in: str, check_out: str) -> Tuple[bool, str]:
    """Validate date range for booking."""
    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        
        # Check-in must be in the future
        today = local_now().replace(hour=0, minute=0, second=0, microsecond=0)
        if check_in_date < today:
            return False, "Check-in date must be in the future"
        
        # Check-out must be after check-in
        if check_out_date <= check_in_date:
            return False, "Check-out must be after check-in"
        
        # Check stay duration
        stay_days = (check_out_date - check_in_date).days
        if stay_days < 1:
            return False, "Minimum stay is 1 day"
        if stay_days > 30:
            return False, "Maximum stay is 30 days"
        
        return True, "Valid dates"
        
    except ValueError as e:
        return False, f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
    except Exception as e:
        return False, str(e)


def validate_room_type(room_type: str) -> bool:
    """Validate room type."""
    if not room_type or not isinstance(room_type, str):
        return False
    valid_types = ['STANDARD', 'DELUXE', 'SUITE', 'PENTHOUSE']
    return room_type.upper() in valid_types


def validate_guest_count(guest_count: Union[int, str]) -> Tuple[bool, str]:
    """Validate number of guests."""
    try:
        count = int(guest_count)
        if count <= 0:
            return False, "Guest count must be at least 1"
        if count > 8:
            return False, "Maximum guests per room is 8"
        return True, "Valid guest count"
    except (ValueError, TypeError):
        return False, "Guest count must be a number"


def validate_positive_number(value: Union[int, float, str], field_name: str = "Amount") -> Tuple[bool, str]:
    """Validate that a value is a positive number."""
    try:
        amount = float(value)
        if amount <= 0:
            return False, f"{field_name} must be greater than 0"
        return True, "Valid amount"
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"


# ============================================
# Sanitization Functions
# ============================================

def sanitize_input(input_str: Optional[Any]) -> str:
    """
    Sanitize string input - removes dangerous characters and strips whitespace.
    """
    if input_str is None:
        return ""
    
    value = str(input_str)
    value = html.escape(value)
    value = value.strip()
    value = value.replace('\x00', '')
    value = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    
    return value


def sanitize_email(email: Optional[str]) -> str:
    """Sanitize email address."""
    if not email:
        return ""
    email = sanitize_input(email)
    email = email.lower()
    email = email.replace(' ', '')
    return email


def sanitize_phone(phone: Optional[str]) -> str:
    """Sanitize phone number."""
    if not phone:
        return ""
    phone = sanitize_input(phone)
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    phone = re.sub(r'[^0-9+]', '', phone)
    return phone


def sanitize_name(name: Optional[str]) -> str:
    """Sanitize a name."""
    if not name:
        return ""
    name = sanitize_input(name)
    name = re.sub(r'[^a-zA-Z\s\-\'\.]', '', name)
    name = ' '.join(word.capitalize() for word in name.split())
    return name


def sanitize_text(text: Optional[str], max_length: int = 1000) -> str:
    """Sanitize free text input."""
    if not text:
        return ""
    text = sanitize_input(text)
    text = re.sub(r'\s+', ' ', text)
    if len(text) > max_length:
        text = text[:max_length]
    return text


def sanitize_address(address: Optional[str]) -> str:
    """Sanitize address."""
    if not address:
        return ""
    address = sanitize_input(address)
    address = re.sub(r'[^a-zA-Z0-9\s\-\.,#/]', '', address)
    return address


def sanitize_number(value: Optional[Any], default: int = 0) -> int:
    """Sanitize a number input."""
    if value is None:
        return default
    try:
        if isinstance(value, str):
            value = re.sub(r'[^0-9-]', '', value)
        return int(value)
    except (ValueError, TypeError):
        return default


def sanitize_float(value: Optional[Any], default: float = 0.0) -> float:
    """Sanitize a float input."""
    if value is None:
        return default
    try:
        if isinstance(value, str):
            value = re.sub(r'[^0-9.-]', '', value)
        return float(value)
    except (ValueError, TypeError):
        return default


# ============================================
# ID Sanitization Functions
# ============================================

def sanitize_guest_id(guest_id: Optional[Any]) -> int:
    """
    Sanitize guest ID.
    
    Args:
        guest_id: Guest ID to sanitize
        
    Returns:
        int: Sanitized guest ID
        
    Raises:
        ValidationError: If guest ID is invalid
    """
    from utils.error_handler import ValidationError
    
    if guest_id is None:
        raise ValidationError("Guest ID is required", field="guest_id")
    
    try:
        sanitized = int(guest_id)
        if sanitized <= 0:
            raise ValidationError("Guest ID must be positive", field="guest_id")
        return sanitized
    except (ValueError, TypeError):
        raise ValidationError("Invalid guest ID format", field="guest_id")


def sanitize_room_id(room_id: Optional[Any]) -> int:
    """
    Sanitize room ID.
    
    Args:
        room_id: Room ID to sanitize
        
    Returns:
        int: Sanitized room ID
        
    Raises:
        ValidationError: If room ID is invalid
    """
    from utils.error_handler import ValidationError
    
    if room_id is None:
        raise ValidationError("Room ID is required", field="room_id")
    
    try:
        sanitized = int(room_id)
        if sanitized <= 0:
            raise ValidationError("Room ID must be positive", field="room_id")
        return sanitized
    except (ValueError, TypeError):
        raise ValidationError("Invalid room ID format", field="room_id")


def sanitize_booking_id(booking_id: Optional[Any]) -> int:
    """
    Sanitize booking ID.
    
    Args:
        booking_id: Booking ID to sanitize
        
    Returns:
        int: Sanitized booking ID
        
    Raises:
        ValidationError: If booking ID is invalid
    """
    from utils.error_handler import ValidationError
    
    if booking_id is None:
        raise ValidationError("Booking ID is required", field="booking_id")
    
    try:
        sanitized = int(booking_id)
        if sanitized <= 0:
            raise ValidationError("Booking ID must be positive", field="booking_id")
        return sanitized
    except (ValueError, TypeError):
        raise ValidationError("Invalid booking ID format", field="booking_id")


def sanitize_guest_count(guest_count: Optional[Any]) -> int:
    """
    Sanitize and validate guest count.
    
    Args:
        guest_count: Guest count to sanitize
        
    Returns:
        int: Sanitized guest count
        
    Raises:
        ValidationError: If guest count is invalid
    """
    from utils.error_handler import ValidationError
    
    try:
        count = int(guest_count) if guest_count is not None else 1
        if count < 1:
            raise ValidationError("Guest count must be at least 1", field="guest_count")
        if count > 8:
            raise ValidationError("Maximum guests per room is 8", field="guest_count")
        return count
    except (ValueError, TypeError):
        raise ValidationError("Guest count must be a number", field="guest_count")


def sanitize_amount(amount: Optional[Any]) -> float:
    """
    Sanitize and validate payment amount.
    
    Args:
        amount: Amount to sanitize
        
    Returns:
        float: Sanitized amount
        
    Raises:
        ValidationError: If amount is invalid
    """
    from utils.error_handler import ValidationError
    
    try:
        sanitized = float(amount) if amount is not None else 0.0
        if sanitized <= 0:
            raise ValidationError("Amount must be greater than 0", field="amount")
        return round(sanitized, 2)
    except (ValueError, TypeError):
        raise ValidationError("Invalid amount format", field="amount")