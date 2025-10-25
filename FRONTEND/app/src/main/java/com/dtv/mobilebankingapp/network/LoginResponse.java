package com.dtv.mobilebankingapp.network;

// File này phải khớp 100% với schemas.Token của FastAPI
public class LoginResponse {
    String token;

    // Getter để lấy token ra
    public String getToken() {
        return token;
    }
}
