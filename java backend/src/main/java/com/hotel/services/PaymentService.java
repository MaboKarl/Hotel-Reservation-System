package com.hotel.services;

import com.hotel.models.Booking;
import com.hotel.models.Payment;
import com.hotel.utils.Validator;
import com.hotel.utils.ErrorHandler.PaymentException;
import com.hotel.utils.ErrorHandler.ValidationException;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

public class PaymentService {
    private final Map<Integer, Payment> payments = new HashMap<>();
    private final AtomicInteger idCounter = new AtomicInteger(1);
    private final BookingService bookingService;
    
    private static final Set<String> PAYMENT_METHODS = Set.of("Credit Card", "Cash", "Bank Transfer", "GCash", "PayPal");
    
    public PaymentService(BookingService bookingService) {
        this.bookingService = bookingService;
    }
    
    public Payment processPayment(int bookingId, double amount, String paymentMethod) {
        Booking booking = bookingService.getBooking(bookingId);
        
        if (booking.getPaymentId() != null) {
            throw new PaymentException("Payment already exists for this booking");
        }
        
        if ("CANCELLED".equals(booking.getStatus())) {
            throw new PaymentException("Cannot process payment for a cancelled booking");
        }
        
        if (amount <= 0) {
            throw new ValidationException("Payment amount must be greater than 0");
        }
        
        if (Math.abs(amount - booking.getTotalAmount()) > 0.01) {
            throw new PaymentException("Payment amount " + amount + 
                " does not match booking total " + booking.getTotalAmount());
        }
        
        if (!PAYMENT_METHODS.contains(paymentMethod)) {
            throw new ValidationException("Invalid payment method: " + paymentMethod);
        }
        
        int paymentId = idCounter.getAndIncrement();
        Payment payment = new Payment();
        payment.setPaymentId(paymentId);
        payment.setBookingId(bookingId);
        payment.setAmount(amount);
        payment.setPaymentMethod(paymentMethod);
        payment.setStatus("PAID");
        payment.setTransactionDate(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        
        payments.put(paymentId, payment);
        
        // Update booking
        bookingService.setPaymentId(bookingId, paymentId);
        
        return payment;
    }
    
    public Payment refundPayment(int paymentId) {
        Payment payment = getPayment(paymentId);
        
        if ("REFUNDED".equals(payment.getStatus())) {
            throw new PaymentException("Payment has already been refunded");
        }
        if (!"PAID".equals(payment.getStatus())) {
            throw new PaymentException("Cannot refund a payment with status: " + payment.getStatus());
        }
        
        payment.setStatus("REFUNDED");
        payment.setRefundDate(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        payments.put(paymentId, payment);
        
        // Update booking
        Booking booking = bookingService.getBooking(payment.getBookingId());
        booking.setPaymentId(null);
        
        return payment;
    }
    
    public Payment getPayment(int paymentId) {
        Payment payment = payments.get(paymentId);
        if (payment == null) {
            throw new PaymentException("Payment with ID " + paymentId + " not found");
        }
        return payment;
    }
    
    public Map<Integer, Payment> getAllPayments() {
        return new HashMap<>(payments);
    }
    
    public Payment getBookingPayment(int bookingId) {
        Booking booking = bookingService.getBooking(bookingId);
        if (booking.getPaymentId() == null) {
            return null;
        }
        return getPayment(booking.getPaymentId());
    }
}