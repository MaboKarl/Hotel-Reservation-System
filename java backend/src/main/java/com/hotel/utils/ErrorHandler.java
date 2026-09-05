package com.hotel.utils;

public class ErrorHandler {
    public static class HotelException extends RuntimeException {
        public HotelException(String message) {
            super(message);
        }
    }
    
    public static class GuestException extends HotelException {
        public GuestException(String message) {
            super(message);
        }
    }
    
    public static class RoomException extends HotelException {
        public RoomException(String message) {
            super(message);
        }
    }
    
    public static class BookingException extends HotelException {
        public BookingException(String message) {
            super(message);
        }
    }
    
    public static class PaymentException extends HotelException {
        public PaymentException(String message) {
            super(message);
        }
    }
    
    public static class ValidationException extends HotelException {
        public ValidationException(String message) {
            super(message);
        }
    }
}