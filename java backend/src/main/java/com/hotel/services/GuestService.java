package com.hotel.services;

import com.hotel.models.Guest;
import com.hotel.utils.Validator;
import com.hotel.utils.ErrorHandler.GuestException;
import com.hotel.utils.ErrorHandler.ValidationException;

import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

public class GuestService {
    private final Map<Integer, Guest> guests = new HashMap<>();
    private final AtomicInteger idCounter = new AtomicInteger(1);
    
    public Guest createGuest(String firstName, String lastName, String email, String phone, String address) {
        // Validate
        if (firstName == null || firstName.trim().isEmpty()) {
            throw new ValidationException("First name is required");
        }
        if (lastName == null || lastName.trim().isEmpty()) {
            throw new ValidationException("Last name is required");
        }
        if (!Validator.isValidEmail(email)) {
            throw new ValidationException("Invalid email format: " + email);
        }
        if (!Validator.isValidPhone(phone)) {
            throw new ValidationException("Invalid phone number: " + phone);
        }
        
        // Check duplicate email
        for (Guest g : guests.values()) {
            if (g.getEmail().equalsIgnoreCase(email)) {
                throw new GuestException("Guest with email " + email + " already exists");
            }
        }
        
        int guestId = idCounter.getAndIncrement();
        Guest guest = new Guest(guestId, firstName.trim(), lastName.trim(), email, phone);
        guest.setAddress(address != null ? address.trim() : "");
        
        guests.put(guestId, guest);
        return guest;
    }
    
    public Guest getGuest(int guestId) {
        Guest guest = guests.get(guestId);
        if (guest == null) {
            throw new GuestException("Guest with ID " + guestId + " not found");
        }
        return guest;
    }
    
    public Guest updateGuest(int guestId, Map<String, Object> updates) {
        Guest guest = getGuest(guestId);
        
        if (updates.containsKey("firstName")) {
            String value = (String) updates.get("firstName");
            if (value != null && !value.trim().isEmpty()) {
                guest.setFirstName(value.trim());
            }
        }
        if (updates.containsKey("lastName")) {
            String value = (String) updates.get("lastName");
            if (value != null && !value.trim().isEmpty()) {
                guest.setLastName(value.trim());
            }
        }
        if (updates.containsKey("email")) {
            String email = (String) updates.get("email");
            if (email != null) {
                if (!Validator.isValidEmail(email)) {
                    throw new ValidationException("Invalid email format: " + email);
                }
                // Check duplicate
                for (Map.Entry<Integer, Guest> entry : guests.entrySet()) {
                    if (entry.getKey() != guestId && entry.getValue().getEmail().equalsIgnoreCase(email)) {
                        throw new GuestException("Guest with email " + email + " already exists");
                    }
                }
                guest.setEmail(email);
            }
        }
        if (updates.containsKey("phone")) {
            String phone = (String) updates.get("phone");
            if (phone != null) {
                if (!Validator.isValidPhone(phone)) {
                    throw new ValidationException("Invalid phone number: " + phone);
                }
                guest.setPhone(phone);
            }
        }
        if (updates.containsKey("address")) {
            String address = (String) updates.get("address");
            if (address != null) {
                guest.setAddress(address.trim());
            }
        }
        
        guests.put(guestId, guest);
        return guest;
    }
    
    public boolean deleteGuest(int guestId) {
        Guest guest = getGuest(guestId);
        
        // Check for active bookings
        if (!guest.getBookings().isEmpty()) {
            // In a real implementation, you'd check if any bookings are active
            // For simplicity, we'll just warn
            throw new GuestException("Cannot delete guest with booking history");
        }
        
        guests.remove(guestId);
        return true;
    }
    
    public Map<Integer, Guest> getAllGuests() {
        return new HashMap<>(guests);
    }
    
    public Map<Integer, Guest> searchGuests(String searchTerm) {
        if (searchTerm == null || searchTerm.trim().isEmpty()) {
            return getAllGuests();
        }
        
        String term = searchTerm.toLowerCase().trim();
        return guests.entrySet().stream()
            .filter(entry -> {
                Guest g = entry.getValue();
                return g.getFirstName().toLowerCase().contains(term) ||
                       g.getLastName().toLowerCase().contains(term) ||
                       g.getEmail().toLowerCase().contains(term) ||
                       g.getPhone().contains(term);
            })
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }
    
    public void addBookingToGuest(int guestId, int bookingId) {
        Guest guest = getGuest(guestId);
        guest.addBooking(bookingId);
        guests.put(guestId, guest);
    }
    
    public void addLoyaltyPoints(int guestId, int points) {
        Guest guest = getGuest(guestId);
        guest.addLoyaltyPoints(points);
        guests.put(guestId, guest);
    }
}