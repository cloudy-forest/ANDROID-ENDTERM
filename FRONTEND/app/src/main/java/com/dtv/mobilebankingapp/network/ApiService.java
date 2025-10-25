package com.dtv.mobilebankingapp.network;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;
import retrofit2.http.GET;
import retrofit2.http.Header;

public interface ApiService {

    // Định nghĩa API đăng nhập
    @POST("/api/auth/login")
    Call<LoginResponse> login(@Body LoginRequest loginRequest);

    @GET("/api/users/me")
    Call<User> getMe(@Header("Authorization") String token);
    // TODO: Thêm API đăng ký và các API khác ở đây

    @GET("/api/accounts/me")
    Call<List<Account>> getMyAccounts(@Header("Authorization") String token);
}
