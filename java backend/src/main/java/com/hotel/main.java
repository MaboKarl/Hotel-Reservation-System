package com.hotel;

import com.google.gson.Gson;
import com.hotel.controllers.*;
import com.hotel.models.*;
import com.hotel.services.*;
import spark.Spark;

import static spark.Spark.*;

public class Main {
    private static final Gson gson = new Gson();
    
    public static void main(String[] args) {
        // Configure Spark
        port(8080);
        enableCORS();
        
        // Initialize services
        GuestService guestService = new GuestService();
        RoomService roomService = new RoomService();
        BookingService bookingService = new BookingService(guestService, roomService);
        PaymentService paymentService = new PaymentService(bookingService);
        ReportService reportService = new ReportService(guestService, roomService, bookingService, paymentService);
        
        // Initialize controllers
        GuestController guestController = new GuestController(guestService, gson);
        RoomController roomController = new RoomController(roomService, gson);
        BookingController bookingController = new BookingController(bookingService, gson);
        PaymentController paymentController = new PaymentController(paymentService, gson);
        ReportController reportController = new ReportController(reportService, gson);
        
        // Setup routes
        setupRoutes(guestController, roomController, bookingController, 
                   paymentController, reportController);
        
        System.out.println("Java Hotel Management System (OOP) running on http://localhost:8080");
    }
    
    private static void setupRoutes(GuestController gc, RoomController rc, 
                                   BookingController bc, PaymentController pc, 
                                   ReportController rptc) {
        // Health check
        get("/api/health", (req, res) -> {
            res.type("application/json");
            return "{\"status\": \"healthy\", \"backend\": \"Java (OOP)\"}";
        });
        
        // Guest routes
        get("/api/guests", gc::getAllGuests);
        post("/api/guests", gc::createGuest);
        get("/api/guests/:id", gc::getGuest);
        put("/api/guests/:id", gc::updateGuest);
        delete("/api/guests/:id", gc::deleteGuest);
        get("/api/guests/search", gc::searchGuests);
        
        // Room routes
        get("/api/rooms", rc::getAllRooms);
        post("/api/rooms", rc::createRoom);
        get("/api/rooms/available", rc::getAvailableRooms);
        get("/api/rooms/:id", rc::getRoom);
        put("/api/rooms/:id", rc::updateRoom);
        delete("/api/rooms/:id", rc::deleteRoom);
        
        // Booking routes
        get("/api/bookings", bc::getAllBookings);
        post("/api/bookings", bc::createBooking);
        post("/api/bookings/check-in", bc::checkIn);
        post("/api/bookings/check-out", bc::checkOut);
        post("/api/bookings/cancel", bc::cancelBooking);
        get("/api/bookings/:id", bc::getBooking);
        get("/api/bookings/current", bc::getCurrentCheckIns);
        get("/api/bookings/guest/:guestId", bc::getGuestBookings);
        
        // Payment routes
        get("/api/payments", pc::getAllPayments);
        post("/api/payments", pc::processPayment);
        get("/api/payments/:id", pc::getPayment);
        post("/api/payments/refund", pc::refundPayment);
        
        // Report routes
        get("/api/reports/occupancy", rptc::getOccupancyReport);
        get("/api/reports/revenue", rptc::getRevenueReport);
        get("/api/reports/guests", rptc::getGuestReport);
        get("/api/reports/bookings", rptc::getBookingReport);
        get("/api/reports/full", rptc::getFullReport);
    }
    
    private static void enableCORS() {
        options("/*", (request, response) -> {
            String accessControlRequestHeaders = request.headers("Access-Control-Request-Headers");
            if (accessControlRequestHeaders != null) {
                response.header("Access-Control-Allow-Headers", accessControlRequestHeaders);
            }
            String accessControlRequestMethod = request.headers("Access-Control-Request-Method");
            if (accessControlRequestMethod != null) {
                response.header("Access-Control-Allow-Methods", accessControlRequestMethod);
            }
            return "OK";
        });
        
        after((request, response) -> {
            response.header("Access-Control-Allow-Origin", "*");
            response.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
            response.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
        });
    }
}