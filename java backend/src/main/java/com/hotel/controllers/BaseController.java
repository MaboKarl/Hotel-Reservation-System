package com.hotel.controllers;

import com.google.gson.Gson;
import spark.Request;
import spark.Response;

public abstract class BaseController {
    protected final Gson gson;
    
    public BaseController(Gson gson) {
        this.gson = gson;
    }
    
    protected String jsonResponse(Object data) {
        return gson.toJson(data);
    }
    
    protected String errorResponse(String message) {
        return gson.toJson(Map.of("error", message));
    }
    
    protected <T> T parseBody(Request req, Class<T> clazz) {
        return gson.fromJson(req.body(), clazz);
    }
}