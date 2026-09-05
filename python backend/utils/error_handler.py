"""
Custom error handling for the Hotel Management System

This module defines a hierarchy of custom exceptions for the hotel management system.
All exceptions inherit from HotelError, which inherits from the built-in Exception class.
"""

from typing import Optional, Dict, Any, Union


class HotelError(Exception):
    """
    Base exception class for all hotel management system errors.
    
    All custom exceptions in the system should inherit from this class
    to allow for catching any hotel-related error.
    
    Example:
        >>> try:
        ...     raise HotelError("Something went wrong")
        ... except HotelError as e:
        ...     print(f"Hotel error: {e}")
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a hotel error.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for categorization
            details: Optional additional details about the error
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary for JSON serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the error
        """
        result: Dict[str, Any] = {
            'error': self.message,
            'type': self.__class__.__name__
        }
        if self.error_code:
            result['error_code'] = self.error_code
        if self.details:
            result['details'] = self.details
        return result
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class GuestError(HotelError):
    """
    Exception raised for guest-related errors.
    
    Examples:
        - Guest not found
        - Duplicate email
        - Guest has active bookings
    """
    
    def __init__(self, message: str, error_code: str = "GUEST_ERROR", **kwargs):
        """
        Initialize a guest error.
        
        Args:
            message: Human-readable error message
            error_code: Error code (defaults to "GUEST_ERROR")
            **kwargs: Additional arguments passed to HotelError
        """
        super().__init__(message, error_code=error_code, **kwargs)


class RoomError(HotelError):
    """
    Exception raised for room-related errors.
    
    Examples:
        - Room not found
        - Room already exists
        - Room is not available
        - Room has booking history
    """
    
    def __init__(self, message: str, error_code: str = "ROOM_ERROR", **kwargs):
        """
        Initialize a room error.
        
        Args:
            message: Human-readable error message
            error_code: Error code (defaults to "ROOM_ERROR")
            **kwargs: Additional arguments passed to HotelError
        """
        super().__init__(message, error_code=error_code, **kwargs)


class BookingError(HotelError):
    """
    Exception raised for booking-related errors.
    
    Examples:
        - Booking not found
        - Room not available for booking
        - Cannot cancel checked-in booking
        - Cannot check-in before date
    """
    
    def __init__(self, message: str, error_code: str = "BOOKING_ERROR", **kwargs):
        """
        Initialize a booking error.
        
        Args:
            message: Human-readable error message
            error_code: Error code (defaults to "BOOKING_ERROR")
            **kwargs: Additional arguments passed to HotelError
        """
        super().__init__(message, error_code=error_code, **kwargs)


class PaymentError(HotelError):
    """
    Exception raised for payment-related errors.
    
    Examples:
        - Payment not found
        - Payment already exists
        - Invalid payment amount
        - Cannot refund payment
    """
    
    def __init__(self, message: str, error_code: str = "PAYMENT_ERROR", **kwargs):
        """
        Initialize a payment error.
        
        Args:
            message: Human-readable error message
            error_code: Error code (defaults to "PAYMENT_ERROR")
            **kwargs: Additional arguments passed to HotelError
        """
        super().__init__(message, error_code=error_code, **kwargs)


class ValidationError(HotelError):
    """
    Exception raised for validation errors.
    
    Examples:
        - Invalid email format
        - Invalid phone number
        - Invalid date range
        - Invalid room type
        - Invalid guest count
    """
    
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR", field: Optional[str] = None, **kwargs):
        """
        Initialize a validation error.
        
        Args:
            message: Human-readable error message
            error_code: Error code (defaults to "VALIDATION_ERROR")
            field: Optional field name that caused the validation error
            **kwargs: Additional arguments passed to HotelError
        """
        self.field = field
        if field and 'details' not in kwargs:
            kwargs['details'] = {'field': field}
        super().__init__(message, error_code=error_code, **kwargs)


class AuthorizationError(HotelError):
    """
    Exception raised for authorization/authentication errors.
    
    Examples:
        - Invalid token
        - Insufficient permissions
        - Session expired
    """
    
    def __init__(self, message: str, error_code: str = "AUTH_ERROR", **kwargs):
        """
        Initialize an authorization error.
        
        Args:
            message: Human-readable error message
            error_code: Error code (defaults to "AUTH_ERROR")
            **kwargs: Additional arguments passed to HotelError
        """
        super().__init__(message, error_code=error_code, **kwargs)


class NotFoundError(HotelError):
    """
    Exception raised when a resource is not found.
    
    Examples:
        - Guest not found
        - Room not found
        - Booking not found
        - Payment not found
    """
    
    def __init__(self, resource: str, resource_id: Union[int, str], error_code: str = "NOT_FOUND", **kwargs):
        """
        Initialize a not found error.
        
        Args:
            resource: Name of the resource (e.g., "Guest", "Room")
            resource_id: ID of the resource that was not found
            error_code: Error code (defaults to "NOT_FOUND")
            **kwargs: Additional arguments passed to HotelError
        """
        message = f"{resource} with ID {resource_id} not found"
        details = {'resource': resource, 'resource_id': resource_id}
        if 'details' in kwargs:
            details.update(kwargs['details'])
        super().__init__(message, error_code=error_code, details=details, **kwargs)


class ConflictError(HotelError):
    """
    Exception raised when a conflict occurs (duplicate resource, etc.).
    
    Examples:
        - Duplicate email
        - Duplicate room number
        - Booking already exists
    """
    
    def __init__(self, message: str, error_code: str = "CONFLICT", **kwargs):
        """
        Initialize a conflict error.
        
        Args:
            message: Human-readable error message
            error_code: Error code (defaults to "CONFLICT")
            **kwargs: Additional arguments passed to HotelError
        """
        super().__init__(message, error_code=error_code, **kwargs)


class DatabaseError(HotelError):
    """
    Exception raised for database/storage errors.
    
    Examples:
        - Failed to save data
        - Failed to load data
        - Corrupted data file
        - Storage full
    """
    
    def __init__(self, message: str, error_code: str = "DB_ERROR", **kwargs):
        """
        Initialize a database error.
        
        Args:
            message: Human-readable error message
            error_code: Error code (defaults to "DB_ERROR")
            **kwargs: Additional arguments passed to HotelError
        """
        super().__init__(message, error_code=error_code, **kwargs)


# ============================================
# FIXED: Helper functions for error handling
# ============================================

def handle_error(error: Exception) -> Dict[str, Any]:
    """
    Convert any exception to a standardized error dictionary.
    
    Args:
        error: The exception to handle
        
    Returns:
        Dict[str, Any]: Standardized error dictionary
        
    Example:
        >>> try:
        ...     raise GuestError("Guest not found")
        ... except Exception as e:
        ...     error_dict = handle_error(e)
        ...     print(error_dict['error'])
        Guest not found
    """
    if isinstance(error, HotelError):
        return error.to_dict()
    else:
        return {
            'error': str(error),
            'type': error.__class__.__name__,
            'error_code': 'UNKNOWN_ERROR'
        }


def create_error_response(error: Exception, status_code: int = 400) -> tuple:
    """
    Create a standardized error response for Flask.
    
    Args:
        error: The exception to handle
        status_code: HTTP status code (defaults to 400)
        
    Returns:
        tuple: (error_dict, status_code)
        
    Example:
        >>> error = GuestError("Guest not found")
        >>> response, status = create_error_response(error, 404)
        >>> response['error']
        'Guest not found'
    """
    if isinstance(error, HotelError):
        return error.to_dict(), status_code
    else:
        return {
            'error': str(error),
            'type': error.__class__.__name__,
            'error_code': 'UNKNOWN_ERROR'
        }, 500


def is_hotel_error(error: Exception) -> bool:
    """
    Check if an exception is a hotel management system error.
    
    Args:
        error: The exception to check
        
    Returns:
        bool: True if the exception is a HotelError, False otherwise
        
    Example:
        >>> is_hotel_error(GuestError("Error"))
        True
        >>> is_hotel_error(ValueError("Error"))
        False
    """
    return isinstance(error, HotelError)


def get_error_code(error: Exception) -> str:
    """
    Get the error code from a hotel error.
    
    Args:
        error: The exception to check
        
    Returns:
        str: Error code if available, otherwise "UNKNOWN_ERROR"
    """
    if isinstance(error, HotelError) and error.error_code:
        return error.error_code
    return "UNKNOWN_ERROR"


# ============================================
# FIXED: Error type mappings for HTTP status codes
# ============================================

ERROR_STATUS_MAP: Dict[type, int] = {
    NotFoundError: 404,
    ValidationError: 400,
    ConflictError: 409,
    AuthorizationError: 401,
    GuestError: 400,
    RoomError: 400,
    BookingError: 400,
    PaymentError: 400,
    DatabaseError: 500
}


def get_status_code_for_error(error: Exception) -> int:
    """
    Get the appropriate HTTP status code for an error.
    
    Args:
        error: The exception to check
        
    Returns:
        int: HTTP status code
        
    Example:
        >>> get_status_code_for_error(NotFoundError("Guest not found"))
        404
    """
    error_class = error.__class__
    for error_type, status_code in ERROR_STATUS_MAP.items():
        if isinstance(error, error_type):
            return status_code
    return 500