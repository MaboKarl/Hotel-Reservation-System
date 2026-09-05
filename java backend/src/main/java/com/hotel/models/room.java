package com.hotel.models;

import java.util.ArrayList;
import java.util.List;

public class Room {
    private int roomId;
    private int roomNumber;
    private String roomType;
    private int floor;
    private String status;
    private Integer currentBooking;
    private List<Integer> bookings;
    
    public Room() {
        this.bookings = new ArrayList<>();
        this.status = "AVAILABLE";
    }
    
    public Room(int roomId, int roomNumber, String roomType, int floor) {
        this();
        this.roomId = roomId;
        this.roomNumber = roomNumber;
        this.roomType = roomType;
        this.floor = floor;
    }
    
    // Getters and Setters
    public int getRoomId() { return roomId; }
    public void setRoomId(int roomId) { this.roomId = roomId; }
    
    public int getRoomNumber() { return roomNumber; }
    public void setRoomNumber(int roomNumber) { this.roomNumber = roomNumber; }
    
    public String getRoomType() { return roomType; }
    public void setRoomType(String roomType) { this.roomType = roomType; }
    
    public int getFloor() { return floor; }
    public void setFloor(int floor) { this.floor = floor; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public Integer getCurrentBooking() { return currentBooking; }
    public void setCurrentBooking(Integer currentBooking) { this.currentBooking = currentBooking; }
    
    public List<Integer> getBookings() { return bookings; }
    public void setBookings(List<Integer> bookings) { this.bookings = bookings; }
    
    public void addBooking(int bookingId) {
        if (!this.bookings.contains(bookingId)) {
            this.bookings.add(bookingId);
        }
    }
    
    public boolean isAvailable() {
        return "AVAILABLE".equals(status);
    }
    
    public boolean isBooked() {
        return "BOOKED".equals(status);
    }
}