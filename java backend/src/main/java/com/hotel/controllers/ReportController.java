package com.hotel.controllers;

import com.google.gson.Gson;
import com.hotel.services.ReportService;
import spark.Request;
import spark.Response;

public class ReportController extends BaseController {
    private final ReportService reportService;
    
    public ReportController(ReportService reportService, Gson gson) {
        super(gson);
        this.reportService = reportService;
    }
    
    public Object getOccupancyReport(Request req, Response res) {
        try {
            res.type("application/json");
            return jsonResponse(reportService.generateOccupancyReport());
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getRevenueReport(Request req, Response res) {
        try {
            String startDate = req.queryParams("start_date");
            String endDate = req.queryParams("end_date");
            res.type("application/json");
            return jsonResponse(reportService.generateRevenueReport(startDate, endDate));
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getGuestReport(Request req, Response res) {
        try {
            res.type("application/json");
            return jsonResponse(reportService.generateGuestReport());
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getBookingReport(Request req, Response res) {
        try {
            res.type("application/json");
            return jsonResponse(reportService.generateBookingReport());
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
    
    public Object getFullReport(Request req, Response res) {
        try {
            res.type("application/json");
            return jsonResponse(reportService.generateFullReport());
        } catch (Exception e) {
            res.status(500);
            return errorResponse(e.getMessage());
        }
    }
}