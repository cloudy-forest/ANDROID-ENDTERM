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

    @POST("/api/transactions/transfer")
    Call<TransactionResponse> performTransfer(
            @Header("Authorization") String token,
            @Body TransferRequest transferRequest
    );

    // API yêu cầu OTP để tạo PIN
    @POST("/api/pin/request-otp")
    Call<MessageResponse> requestPinOtp(@Header("Authorization") String token);

    // API gửi Mật khẩu, OTP, và PIN mới
    @POST("/api/pin/set")
    Call<MessageResponse> setPin(
            @Header("Authorization") String token,
            @Body PinSetRequest pinSetRequest
    );
}
