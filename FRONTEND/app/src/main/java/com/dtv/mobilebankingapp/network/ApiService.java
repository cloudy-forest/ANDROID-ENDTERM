package com.dtv.mobilebankingapp.network;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

public interface ApiService {

    // Định nghĩa API đăng nhập
    @POST("/api/auth/login")
    Call<LoginResponse> login(@Body LoginRequest loginRequest);

    // TODO: Thêm API đăng ký và các API khác ở đây
}