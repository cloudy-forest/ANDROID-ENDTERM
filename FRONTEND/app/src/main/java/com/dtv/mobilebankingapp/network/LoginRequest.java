package com.dtv.mobilebankingapp.network;

// File này phải khớp 100% với schemas.LoginRequest của FastAPI
public class LoginRequest {
    String username;
    String password;

    public LoginRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }
}