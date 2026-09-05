package com.hotel.models;

import java.util.ArrayList;
import java.util.List;

public class Guest {
    private int guestId;
    private String firstName;
    private String lastName;
    private String email;
    private String phone;
    private String address;
    private List<Integer> bookings;
    private int loyaltyPoints;
    
    public Guest() {
        this.bookings = new ArrayList<>();
        this.loyaltyPoints = 0;
    }
    
    public Guest(int guestId, String firstName, String lastName, String email, String phone) {
        this();
        this.guestId = guestId;
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.phone = phone;
    }
    
    // Getters and Setters
    public int getGuestId() { return guestId; }
    public void setGuestId(int guestId) { this.guestId = guestId; }
    
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }
    
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    
    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }
    
    public List<Integer> getBookings() { return bookings; }
    public void setBookings(List<Integer> bookings) { this.bookings = bookings; }
    
    public int getLoyaltyPoints() { return loyaltyPoints; }
    public void setLoyaltyPoints(int loyaltyPoints) { this.loyaltyPoints = loyaltyPoints; }
    
    public void addBooking(int bookingId) {
        if (!this.bookings.contains(bookingId)) {
            this.bookings.add(bookingId);
        }
    }
    
    public void addLoyaltyPoints(int points) {
        this.loyaltyPoints += points;
    }
    
    public String getFullName() {
        return firstName + " " + lastName;
    }
}