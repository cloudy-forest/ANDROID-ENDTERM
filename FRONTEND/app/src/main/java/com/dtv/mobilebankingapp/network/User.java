package com.dtv.mobilebankingapp.network;

public class User {
    private int id;
    private String username;
    private String full_name; // FastAPI dùng 'full_name', Gson sẽ tự động khớp
    private String role;

    // Getters
    public int getId() {
        return id;
    }

    public String getUsername() {
        return username;
    }

    public String getFullName() {
        return full_name;
    }

    public String getRole() {
        return role;
    }
}
