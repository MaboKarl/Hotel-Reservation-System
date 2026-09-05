package com.hotel.controllers;

import com.google.gson.Gson;
import com.hotel.models.Payment;
import com.hotel.services.PaymentService;
import spark.Request;
import spark.Response;

import java.util.Map;

public class PaymentController extends BaseController {
    private final PaymentService paymentService;
    
    public PaymentController(PaymentService paymentService, Gson gson) {
        super(gson);
        this.paymentService = paymentService;
    }
    
    public Object getAllPayments(Request req, Response res) {
        try {
            res.type("application/json");
            return jsonResponse(paymentService.getAllPayments());
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object processPayment(Request req, Response res) {
        try {
            Map<String, Object> data = parseBody(req, Map.class);
            Payment payment = paymentService.processPayment(
                ((Double) data.get("bookingId")).intValue(),
                ((Double) data.get("amount")).doubleValue(),
                (String) data.get("paymentMethod")
            );
            res.status(201);
            res.type("application/json");
            return jsonResponse(payment);
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getPayment(Request req, Response res) {
        try {
            int id = Integer.parseInt(req.params(":id"));
            res.type("application/json");
            return jsonResponse(paymentService.getPayment(id));
        } catch (Exception e) {
            res.status(404);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object refundPayment(Request req, Response res) {
        try {
            Map<String, Object> data = parseBody(req, Map.class);
            int paymentId = ((Double) data.get("paymentId")).intValue();
            res.type("application/json");
            return jsonResponse(paymentService.refundPayment(paymentId));
        } catch (Exception e) {
            res.status(400);
            return errorResponse(e.getMessage());
        }
    }
}