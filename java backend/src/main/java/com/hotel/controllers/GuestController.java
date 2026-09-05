package com.hotel.controllers;

import com.google.gson.Gson;
import com.hotel.models.Guest;
import com.hotel.services.GuestService;
import spark.Request;
import spark.Response;

import java.util.Map;

public class GuestController extends BaseController {
    private final GuestService guestService;
    
    public GuestController(GuestService guestService, Gson gson) {
        super(gson);
        this.guestService = guestService;
    }
    
    public Object getAllGuests(Request req, Response res) {
        try {
            res.type("application/json");
            return jsonResponse(guestService.getAllGuests());
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object createGuest(Request req, Response res) {
        try {
            Map<String, Object> data = parseBody(req, Map.class);
            Guest guest = guestService.createGuest(
                (String) data.get("firstName"),
                (String) data.get("lastName"),
                (String) data.get("email"),
                (String) data.get("phone"),
                (String) data.get("address")
            );
            res.status(201);
            res.type("application/json");
            return jsonResponse(guest);
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getGuest(Request req, Response res) {
        try {
            int id = Integer.parseInt(req.params(":id"));
            res.type("application/json");
            return jsonResponse(guestService.getGuest(id));
        } catch (Exception e) {
            res.status(404);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object updateGuest(Request req, Response res) {
        try {
            int id = Integer.parseInt(req.params(":id"));
            Map<String, Object> data = parseBody(req, Map.class);
            res.type("application/json");
            return jsonResponse(guestService.updateGuest(id, data));
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object deleteGuest(Request req, Response res) {
        try {
            int id = Integer.parseInt(req.params(":id"));
            guestService.deleteGuest(id);
            res.type("application/json");
            return jsonResponse(Map.of("success", true));
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object searchGuests(Request req, Response res) {
        try {
            String searchTerm = req.queryParams("q");
            res.type("application/json");
            return jsonResponse(guestService.searchGuests(searchTerm));
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
}