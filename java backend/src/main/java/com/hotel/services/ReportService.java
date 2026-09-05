package com.hotel.services;

import com.hotel.models.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

public class ReportService {
    private final GuestService guestService;
    private final RoomService roomService;
    private final BookingService bookingService;
    private final PaymentService paymentService;
    
    public ReportService(GuestService guestService, RoomService roomService, 
                        BookingService bookingService, PaymentService paymentService) {
        this.guestService = guestService;
        this.roomService = roomService;
        this.bookingService = bookingService;
        this.paymentService = paymentService;
    }
    
    public Map<String, Object> generateOccupancyReport() {
        Map<Integer, Room> rooms = roomService.getAllRooms();
        int totalRooms = rooms.size();
        int bookedRooms = 0;
        int availableRooms = 0;
        int maintenanceRooms = 0;
        int cleaningRooms = 0;
        
        Map<String, Map<String, Integer>> roomTypeStats = new HashMap<>();
        
        for (Room room : rooms.values()) {
            String type = room.getRoomType();
            roomTypeStats.putIfAbsent(type, new HashMap<>());
            roomTypeStats.get(type).put("total", roomTypeStats.get(type).getOrDefault("total", 0) + 1);
            
            switch (room.getStatus()) {
                case "BOOKED":
                    bookedRooms++;
                    roomTypeStats.get(type).put("booked", 
                        roomTypeStats.get(type).getOrDefault("booked", 0) + 1);
                    break;
                case "AVAILABLE":
                    availableRooms++;
                    roomTypeStats.get(type).put("available", 
                        roomTypeStats.get(type).getOrDefault("available", 0) + 1);
                    break;
                case "MAINTENANCE":
                    maintenanceRooms++;
                    break;
                case "CLEANING":
                    cleaningRooms++;
                    break;
            }
        }
        
        double occupancyRate = totalRooms > 0 ? (double) bookedRooms / totalRooms * 100 : 0;
        
        Map<String, Object> report = new HashMap<>();
        report.put("totalRooms", totalRooms);
        report.put("bookedRooms", bookedRooms);
        report.put("availableRooms", availableRooms);
        report.put("maintenanceRooms", maintenanceRooms);
        report.put("cleaningRooms", cleaningRooms);
        report.put("occupancyRate", occupancyRate);
        report.put("roomTypeStats", roomTypeStats);
        
        return report;
    }
    
    public Map<String, Object> generateRevenueReport(String startDateStr, String endDateStr) {
        LocalDate startDate = startDateStr != null ? LocalDate.parse(startDateStr) : LocalDate.now().minusDays(30);
        LocalDate endDate = endDateStr != null ? LocalDate.parse(endDateStr) : LocalDate.now();
        
        double totalRevenue = 0;
        Map<String, Double> paymentMethods = new HashMap<>();
        int bookingsInRange = 0;
        
        for (Payment payment : paymentService.getAllPayments().values()) {
            if (!"PAID".equals(payment.getStatus())) {
                continue;
            }
            
            LocalDate paymentDate = LocalDate.parse(payment.getTransactionDate().substring(0, 10));
            if ((paymentDate.isAfter(startDate) || paymentDate.equals(startDate)) &&
                (paymentDate.isBefore(endDate) || paymentDate.equals(endDate))) {
                totalRevenue += payment.getAmount();
                bookingsInRange++;
                paymentMethods.put(payment.getPaymentMethod(), 
                    paymentMethods.getOrDefault(payment.getPaymentMethod(), 0.0) + payment.getAmount());
            }
        }
        
        Map<String, Object> report = new HashMap<>();
        report.put("startDate", startDate.toString());
        report.put("endDate", endDate.toString());
        report.put("totalRevenue", totalRevenue);
        report.put("bookingsCount", bookingsInRange);
        report.put("paymentMethods", paymentMethods);
        report.put("averageBookingValue", bookingsInRange > 0 ? totalRevenue / bookingsInRange : 0);
        
        return report;
    }
    
    public Map<String, Object> generateGuestReport() {
        Map<Integer, Guest> guests = guestService.getAllGuests();
        int totalGuests = guests.size();
        int guestsWithBookings = 0;
        int totalLoyaltyPoints = 0;
        
        List<Map<String, Object>> topGuests = new ArrayList<>();
        
        for (Guest guest : guests.values()) {
            int bookingCount = guest.getBookings().size();
            if (bookingCount > 0) {
                guestsWithBookings++;
            }
            totalLoyaltyPoints += guest.getLoyaltyPoints();
            
            Map<String, Object> guestInfo = new HashMap<>();
            guestInfo.put("guestId", guest.getGuestId());
            guestInfo.put("name", guest.getFullName());
            guestInfo.put("bookingCount", bookingCount);
            guestInfo.put("loyaltyPoints", guest.getLoyaltyPoints());
            topGuests.add(guestInfo);
        }
        
        topGuests.sort((a, b) -> Integer.compare((int) b.get("bookingCount"), (int) a.get("bookingCount")));
        topGuests = topGuests.stream().limit(5).collect(java.util.stream.Collectors.toList());
        
        Map<String, Object> report = new HashMap<>();
        report.put("totalGuests", totalGuests);
        report.put("guestsWithBookings", guestsWithBookings);
        report.put("totalLoyaltyPoints", totalLoyaltyPoints);
        report.put("averageLoyaltyPoints", totalGuests > 0 ? (double) totalLoyaltyPoints / totalGuests : 0);
        report.put("topGuests", topGuests);
        
        return report;
    }
    
    public Map<String, Object> generateBookingReport() {
        Map<Integer, Booking> bookings = bookingService.getAllBookings();
        int totalBookings = bookings.size();
        
        Map<String, Integer> statusCounts = new HashMap<>();
        statusCounts.put("CONFIRMED", 0);
        statusCounts.put("CHECKED_IN", 0);
        statusCounts.put("CHECKED_OUT", 0);
        statusCounts.put("CANCELLED", 0);
        
        List<Map<String, Object>> upcomingBookings = new ArrayList<>();
        List<Map<String, Object>> currentBookings = new ArrayList<>();
        LocalDate today = LocalDate.now();
        
        for (Booking booking : bookings.values()) {
            statusCounts.put(booking.getStatus(), statusCounts.getOrDefault(booking.getStatus(), 0) + 1);
            
            LocalDate checkIn = LocalDate.parse(booking.getCheckIn());
            LocalDate checkOut = LocalDate.parse(booking.getCheckOut());
            
            if ("CONFIRMED".equals(booking.getStatus()) && !checkIn.isBefore(today)) {
                Guest guest = guestService.getGuest(booking.getGuestId());
                Map<String, Object> upcoming = new HashMap<>();
                upcoming.put("bookingId", booking.getBookingId());
                upcoming.put("guestName", guest.getFullName());
                upcoming.put("roomNumber", booking.getRoomNumber());
                upcoming.put("checkIn", booking.getCheckIn());
                upcoming.put("checkOut", booking.getCheckOut());
                upcomingBookings.add(upcoming);
            }
            
            if ("CHECKED_IN".equals(booking.getStatus())) {
                Guest guest = guestService.getGuest(booking.getGuestId());
                Map<String, Object> current = new HashMap<>();
                current.put("bookingId", booking.getBookingId());
                current.put("guestName", guest.getFullName());
                current.put("roomNumber", booking.getRoomNumber());
                current.put("checkOut", booking.getCheckOut());
                currentBookings.add(current);
            }
        }
        
        upcomingBookings.sort((a, b) -> ((String) a.get("checkIn")).compareTo((String) b.get("checkIn")));
        
        Map<String, Object> report = new HashMap<>();
        report.put("totalBookings", totalBookings);
        report.put("statusCounts", statusCounts);
        report.put("upcomingBookings", upcomingBookings.stream().limit(5).collect(java.util.stream.Collectors.toList()));
        report.put("currentBookings", currentBookings);
        
        return report;
    }
    
    public Map<String, Object> generateFullReport() {
        Map<String, Object> report = new HashMap<>();
        report.put("occupancy", generateOccupancyReport());
        report.put("revenue", generateRevenueReport(null, null));
        report.put("guests", generateGuestReport());
        report.put("bookings", generateBookingReport());
        report.put("generatedAt", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        return report;
    }
}