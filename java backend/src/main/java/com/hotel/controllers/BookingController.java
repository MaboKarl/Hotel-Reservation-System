package com.hotel.controllers;

import com.google.gson.Gson;
import com.hotel.models.Booking;
import com.hotel.services.BookingService;
import spark.Request;
import spark.Response;

import java.util.Map;

public class BookingController extends BaseController {
    private final BookingService bookingService;
    
    public BookingController(BookingService bookingService, Gson gson) {
        super(gson);
        this.bookingService = bookingService;
    }
    
    public Object getAllBookings(Request req, Response res) {
        try {
            res.type("application/json");
            return jsonResponse(bookingService.getAllBookings());
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object createBooking(Request req, Response res) {
        try {
            Map<String, Object> data = parseBody(req, Map.class);
            Booking booking = bookingService.createBooking(
                ((Double) data.get("guestId")).intValue(),
                ((Double) data.get("roomId")).intValue(),
                (String) data.get("checkIn"),
                (String) data.get("checkOut"),
                ((Double) data.getOrDefault("guestCount", 1.0)).intValue(),
                (String) data.get("specialRequests")
            );
            res.status(201);
            res.type("application/json");
            return jsonResponse(booking);
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object checkIn(Request req, Response res) {
        try {
            Map<String, Object> data = parseBody(req, Map.class);
            int bookingId = ((Double) data.get("bookingId")).intValue();
            res.type("application/json");
            return jsonResponse(bookingService.checkIn(bookingId));
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object checkOut(Request req, Response res) {
        try {
            Map<String, Object> data = parseBody(req, Map.class);
            int bookingId = ((Double) data.get("bookingId")).intValue();
            res.type("application/json");
            return jsonResponse(bookingService.checkOut(bookingId));
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object cancelBooking(Request req, Response res) {
        try {
            Map<String, Object> data = parseBody(req, Map.class);
            int bookingId = ((Double) data.get("bookingId")).intValue();
            res.type("application/json");
            return jsonResponse(bookingService.cancelBooking(bookingId));
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getBooking(Request req, Response res) {
        try {
            int id = Integer.parseInt(req.params(":id"));
            res.type("application/json");
            return jsonResponse(bookingService.getBooking(id));
        } catch (Exception e) {
            res.status(404);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getCurrentCheckIns(Request req, Response res) {
        try {
            res.type("application/json");
            return jsonResponse(bookingService.getCurrentCheckIns());
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getGuestBookings(Request req, Response res) {
        try {
            int guestId = Integer.parseInt(req.params(":guestId"));
            res.type("application/json");
            return jsonResponse(bookingService.getGuestBookings(guestId));
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
}