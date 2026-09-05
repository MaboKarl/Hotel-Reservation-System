package com.hotel.controllers;

import com.google.gson.Gson;
import com.hotel.models.Room;
import com.hotel.services.RoomService;
import spark.Request;
import spark.Response;

import java.util.Map;

public class RoomController extends BaseController {
    private final RoomService roomService;
    
    public RoomController(RoomService roomService, Gson gson) {
        super(gson);
        this.roomService = roomService;
    }
    
    public Object getAllRooms(Request req, Response res) {
        try {
            res.type("application/json");
            return jsonResponse(roomService.getAllRooms());
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object createRoom(Request req, Response res) {
        try {
            Map<String, Object> data = parseBody(req, Map.class);
            Room room = roomService.createRoom(
                ((Double) data.get("roomNumber")).intValue(),
                (String) data.get("roomType"),
                ((Double) data.get("floor")).intValue()
            );
            res.status(201);
            res.type("application/json");
            return jsonResponse(room);
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getAvailableRooms(Request req, Response res) {
        try {
            String roomType = req.queryParams("type");
            res.type("application/json");
            return jsonResponse(roomService.getAvailableRooms(roomType));
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getRoom(Request req, Response res) {
        try {
            int id = Integer.parseInt(req.params(":id"));
            res.type("application/json");
            return jsonResponse(roomService.getRoom(id));
        } catch (Exception e) {
            res.status(404);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object updateRoom(Request req, Response res) {
        try {
            int id = Integer.parseInt(req.params(":id"));
            Map<String, Object> data = parseBody(req, Map.class);
            res.type("application/json");
            return jsonResponse(roomService.updateRoom(id, data));
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object deleteRoom(Request req, Response res) {
        try {
            int id = Integer.parseInt(req.params(":id"));
            roomService.deleteRoom(id);
            res.type("application/json");
            return jsonResponse(Map.of("success", true));
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
}