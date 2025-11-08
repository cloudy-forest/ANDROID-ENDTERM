package com.dtv.mobilebankingapp.network;

public class PinSetRequest {
    String password; // Mật khẩu đăng nhập
    String otp;
    String new_pin;

    public PinSetRequest(String password, String otp, String new_pin) {
        this.password = password;
        this.otp = otp;
        this.new_pin = new_pin;
    }
}
