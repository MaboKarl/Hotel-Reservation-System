package com.hotel.services;

import com.hotel.models.Room;
import com.hotel.utils.Validator;
import com.hotel.utils.ErrorHandler.RoomException;
import com.hotel.utils.ErrorHandler.ValidationException;

import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

public class RoomService {
    private final Map<Integer, Room> rooms = new HashMap<>();
    private final AtomicInteger idCounter = new AtomicInteger(1);
    
    private static final Set<String> ROOM_TYPES = Set.of("STANDARD", "DELUXE", "SUITE", "PENTHOUSE");
    private static final Set<String> STATUSES = Set.of("AVAILABLE", "BOOKED", "MAINTENANCE", "CLEANING");
    private static final Map<String, Integer> CAPACITY = Map.of("STANDARD", 2, "DELUXE", 4, "SUITE", 6, "PENTHOUSE", 8);
    private static final Map<String, Double> BASE_PRICES = Map.of("STANDARD", 100.0, "DELUXE", 200.0, "SUITE", 350.0, "PENTHOUSE", 500.0);
    
    public Room createRoom(int roomNumber, String roomType, int floor) {
        if (!ROOM_TYPES.contains(roomType)) {
            throw new ValidationException("Invalid room type: " + roomType);
        }
        if (roomNumber <= 0 || floor <= 0) {
            throw new ValidationException("Room number and floor must be positive");
        }
        
        // Check duplicate room number
        for (Room r : rooms.values()) {
            if (r.getRoomNumber() == roomNumber) {
                throw new RoomException("Room " + roomNumber + " already exists");
            }
        }
        
        int roomId = idCounter.getAndIncrement();
        Room room = new Room(roomId, roomNumber, roomType, floor);
        rooms.put(roomId, room);
        return room;
    }
    
    public Room getRoom(int roomId) {
        Room room = rooms.get(roomId);
        if (room == null) {
            throw new RoomException("Room with ID " + roomId + " not found");
        }
        return room;
    }
    
    public Room updateRoom(int roomId, Map<String, Object> updates) {
        Room room = getRoom(roomId);
        if (updates.containsKey("roomType")) {
            String value = (String) updates.get("roomType");
            if (value != null && ROOM_TYPES.contains(value)) {
                room.setRoomType(value);
            }
        }
        if (updates.containsKey("status")) {
            String value = (String) updates.get("status");
            if (value != null && STATUSES.contains(value)) {
                room.setStatus(value);
            }
        }
        rooms.put(roomId, room);
        return room;
    }
    
    public boolean deleteRoom(int roomId) {
        Room room = getRoom(roomId);
        if ("BOOKED".equals(room.getStatus())) {
            throw new RoomException("Cannot delete a room that is currently booked");
        }
        if (!room.getBookings().isEmpty()) {
            throw new RoomException("Cannot delete a room with booking history");
        }
        rooms.remove(roomId);
        return true;
    }
    
    public Map<Integer, Room> getAllRooms() {
        return new HashMap<>(rooms);
    }
    
    public Map<Integer, Room> getAvailableRooms(String roomType) {
        return rooms.entrySet().stream()
            .filter(e -> "AVAILABLE".equals(e.getValue().getStatus()))
            .filter(e -> roomType == null || roomType.equals(e.getValue().getRoomType()))
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }
    
    public void setCurrentBooking(int roomId, int bookingId) {
        Room room = getRoom(roomId);
        room.setCurrentBooking(bookingId);
        room.setStatus("BOOKED");
        rooms.put(roomId, room);
    }
    
    public void clearCurrentBooking(int roomId) {
        Room room = getRoom(roomId);
        room.setCurrentBooking(null);
        room.setStatus("AVAILABLE");
        rooms.put(roomId, room);
    }
    
    public void addBookingToRoom(int roomId, int bookingId) {
        Room room = getRoom(roomId);
        room.addBooking(bookingId);
        rooms.put(roomId, room);
    }
    
    public int getRoomCapacity(String roomType) {
        return CAPACITY.getOrDefault(roomType, 2);
    }
    
    public double getRoomBasePrice(String roomType) {
        return BASE_PRICES.getOrDefault(roomType, 100.0);
    }
}