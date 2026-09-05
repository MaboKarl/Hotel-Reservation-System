package com.hotel.services;

import com.hotel.models.Booking;
import com.hotel.models.Guest;
import com.hotel.models.Room;
import com.hotel.utils.Validator;
import com.hotel.utils.ErrorHandler.BookingException;
import com.hotel.utils.ErrorHandler.ValidationException;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

public class BookingService {
    private final Map<Integer, Booking> bookings = new HashMap<>();
    private final AtomicInteger idCounter = new AtomicInteger(1);
    
    private final GuestService guestService;
    private final RoomService roomService;
    
    private static final double TAX_RATE = 0.12;
    private static final double SERVICE_CHARGE_RATE = 0.05;
    private static final Set<String> STATUSES = Set.of("CONFIRMED", "CHECKED_IN", "CHECKED_OUT", "CANCELLED");
    
    public BookingService(GuestService guestService, RoomService roomService) {
        this.guestService = guestService;
        this.roomService = roomService;
    }
    
    public Booking createBooking(int guestId, int roomId, String checkIn, String checkOut, 
                                 int guestCount, String specialRequests) {
        Guest guest = guestService.getGuest(guestId);
        Room room = roomService.getRoom(roomId);
        
        // Validate dates
        if (!Validator.isValidDate(checkIn)) {
            throw new ValidationException("Invalid check-in date format. Use YYYY-MM-DD");
        }
        if (!Validator.isValidDate(checkOut)) {
            throw new ValidationException("Invalid check-out date format. Use YYYY-MM-DD");
        }
        
        LocalDate checkInDate = LocalDate.parse(checkIn);
        LocalDate checkOutDate = LocalDate.parse(checkOut);
        
        if (checkInDate.isBefore(LocalDate.now())) {
            throw new ValidationException("Check-in date must be in the future");
        }
        if (checkOutDate.isBefore(checkInDate) || checkOutDate.equals(checkInDate)) {
            throw new ValidationException("Check-out must be after check-in");
        }
        
        long stayDays = ChronoUnit.DAYS.between(checkInDate, checkOutDate);
        if (stayDays < 1) {
            throw new ValidationException("Minimum stay is 1 day");
        }
        if (stayDays > 30) {
            throw new ValidationException("Maximum stay is 30 days");
        }
        
        // Check room availability
        if (!room.isAvailable()) {
            throw new BookingException("Room " + room.getRoomNumber() + " is not available");
        }
        
        // Check capacity
        int capacity = roomService.getRoomCapacity(room.getRoomType());
        if (guestCount > capacity) {
            throw new BookingException("Room type " + room.getRoomType() + 
                " can only accommodate " + capacity + " guests");
        }
        
        // Calculate cost
        double basePrice = roomService.getRoomBasePrice(room.getRoomType());
        double subtotal = basePrice * stayDays;
        double tax = subtotal * TAX_RATE;
        double serviceCharge = subtotal * SERVICE_CHARGE_RATE;
        double total = subtotal + tax + serviceCharge;
        
        Map<String, Double> costBreakdown = new HashMap<>();
        costBreakdown.put("nights", (double) stayDays);
        costBreakdown.put("roomPrice", basePrice);
        costBreakdown.put("subtotal", subtotal);
        costBreakdown.put("tax", tax);
        costBreakdown.put("serviceCharge", serviceCharge);
        costBreakdown.put("total", total);
        
        // Create booking
        int bookingId = idCounter.getAndIncrement();
        Booking booking = new Booking();
        booking.setBookingId(bookingId);
        booking.setGuestId(guestId);
        booking.setRoomId(roomId);
        booking.setRoomNumber(room.getRoomNumber());
        booking.setRoomType(room.getRoomType());
        booking.setCheckIn(checkIn);
        booking.setCheckOut(checkOut);
        booking.setGuestCount(guestCount);
        booking.setSpecialRequests(specialRequests != null ? specialRequests.trim() : "");
        booking.setStatus("CONFIRMED");
        booking.setCostBreakdown(costBreakdown);
        booking.setTotalAmount(total);
        booking.setCreatedAt(LocalDate.now().toString());
        
        bookings.put(bookingId, booking);
        
        // Update room
        roomService.setCurrentBooking(roomId, bookingId);
        roomService.addBookingToRoom(roomId, bookingId);
        
        // Update guest
        guestService.addBookingToGuest(guestId, bookingId);
        
        return booking;
    }
    
    public Booking getBooking(int bookingId) {
        Booking booking = bookings.get(bookingId);
        if (booking == null) {
            throw new BookingException("Booking with ID " + bookingId + " not found");
        }
        return booking;
    }
    
    public Booking cancelBooking(int bookingId) {
        Booking booking = getBooking(bookingId);
        
        if ("CHECKED_OUT".equals(booking.getStatus())) {
            throw new BookingException("Cannot cancel a booking that has been checked out");
        }
        if ("CANCELLED".equals(booking.getStatus())) {
            throw new BookingException("Booking is already cancelled");
        }
        if ("CHECKED_IN".equals(booking.getStatus())) {
            throw new BookingException("Cannot cancel a booking that has been checked in");
        }
        
        booking.setStatus("CANCELLED");
        bookings.put(bookingId, booking);
        
        // Clear room
        roomService.clearCurrentBooking(booking.getRoomId());
        
        return booking;
    }
    
    public Booking checkIn(int bookingId) {
        Booking booking = getBooking(bookingId);
        
        if ("CHECKED_IN".equals(booking.getStatus())) {
            throw new BookingException("Booking is already checked in");
        }
        if ("CANCELLED".equals(booking.getStatus())) {
            throw new BookingException("Cannot check in a cancelled booking");
        }
        if ("CHECKED_OUT".equals(booking.getStatus())) {
            throw new BookingException("Booking has already been checked out");
        }
        
        LocalDate checkInDate = LocalDate.parse(booking.getCheckIn());
        if (checkInDate.isAfter(LocalDate.now())) {
            throw new BookingException("Cannot check in before the check-in date");
        }
        
        booking.setStatus("CHECKED_IN");
        bookings.put(bookingId, booking);
        return booking;
    }
    
    public Booking checkOut(int bookingId) {
        Booking booking = getBooking(bookingId);
        
        if ("CHECKED_OUT".equals(booking.getStatus())) {
            throw new BookingException("Booking is already checked out");
        }
        if (!"CHECKED_IN".equals(booking.getStatus())) {
            throw new BookingException("Cannot check out a booking with status: " + booking.getStatus());
        }
        
        booking.setStatus("CHECKED_OUT");
        bookings.put(bookingId, booking);
        
        // Clear room
        roomService.clearCurrentBooking(booking.getRoomId());
        
        // Add loyalty points
        int points = (int) (booking.getTotalAmount() / 10);
        guestService.addLoyaltyPoints(booking.getGuestId(), points);
        
        return booking;
    }
    
    public Map<Integer, Booking> getAllBookings() {
        return new HashMap<>(bookings);
    }
    
    public Map<Integer, Booking> getGuestBookings(int guestId) {
        Guest guest = guestService.getGuest(guestId);
        Map<Integer, Booking> result = new HashMap<>();
        for (int bookingId : guest.getBookings()) {
            result.put(bookingId, getBooking(bookingId));
        }
        return result;
    }
    
    public List<Map<String, Object>> getCurrentCheckIns() {
        List<Map<String, Object>> current = new ArrayList<>();
        for (Booking booking : bookings.values()) {
            if ("CHECKED_IN".equals(booking.getStatus())) {
                Guest guest = guestService.getGuest(booking.getGuestId());
                Map<String, Object> checkIn = new HashMap<>();
                checkIn.put("bookingId", booking.getBookingId());
                checkIn.put("guestName", guest.getFullName());
                checkIn.put("roomNumber", booking.getRoomNumber());
                checkIn.put("checkOut", booking.getCheckOut());
                current.add(checkIn);
            }
        }
        return current;
    }
    
    public void setPaymentId(int bookingId, int paymentId) {
        Booking booking = getBooking(bookingId);
        booking.setPaymentId(paymentId);
        bookings.put(bookingId, booking);
    }
}