package com.dtv.mobilebankingapp;

import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.dtv.mobilebankingapp.network.ApiService;
import com.dtv.mobilebankingapp.network.MessageResponse;
import com.dtv.mobilebankingapp.network.PinSetRequest;
import com.dtv.mobilebankingapp.network.RetrofitClient;
import com.dtv.mobilebankingapp.network.SessionManager;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class SetPinActivity extends AppCompatActivity {

    private EditText etPassword, etOtp, etNewPin;
    private Button btnRequestOtp, btnConfirmPin;
    private ApiService apiService;
    private SessionManager sessionManager;
    private String authToken;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_set_pin);

        // Khởi tạo
        apiService = RetrofitClient.getApiService();
        sessionManager = new SessionManager(this);
        authToken = "Bearer " + sessionManager.getAuthToken();

        // Ánh xạ
        etPassword = findViewById(R.id.etPassword);
        etOtp = findViewById(R.id.etOtp);
        etNewPin = findViewById(R.id.etNewPin);
        btnRequestOtp = findViewById(R.id.btnRequestOtp);
        btnConfirmPin = findViewById(R.id.btnConfirmPin);

        // Gán sự kiện
        btnRequestOtp.setOnClickListener(v -> handleRequestOtp());
        btnConfirmPin.setOnClickListener(v -> handleConfirmPin());
    }

    // Hàm gọi API /api/pin/request-otp
    private void handleRequestOtp() {
        btnRequestOtp.setEnabled(false); // Vô hiệu hóa nút
        Toast.makeText(this, "Đang gửi OTP...", Toast.LENGTH_SHORT).show();

        Call<MessageResponse> call = apiService.requestPinOtp(authToken);
        call.enqueue(new Callback<MessageResponse>() {
            @Override
            public void onResponse(Call<MessageResponse> call, Response<MessageResponse> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(SetPinActivity.this, "OTP đã gửi, vui lòng kiểm tra email (Gmail)", Toast.LENGTH_LONG).show();
                } else {
                    Toast.makeText(SetPinActivity.this, "Gửi OTP thất bại", Toast.LENGTH_SHORT).show();
                    btnRequestOtp.setEnabled(true); // Bật lại nút nếu lỗi
                }
            }

            @Override
            public void onFailure(Call<MessageResponse> call, Throwable t) {
                Toast.makeText(SetPinActivity.this, "Lỗi kết nối: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                btnRequestOtp.setEnabled(true); // Bật lại nút nếu lỗi
            }
        });
    }

    // Hàm gọi API /api/pin/set
    private void handleConfirmPin() {
        String password = etPassword.getText().toString();
        String otp = etOtp.getText().toString();
        String newPin = etNewPin.getText().toString();

        // Kiểm tra input
        if (password.isEmpty() || otp.isEmpty() || newPin.isEmpty()) {
            Toast.makeText(this, "Vui lòng nhập đủ thông tin", Toast.LENGTH_SHORT).show();
            return;
        }

        if (newPin.length() != 6) {
            Toast.makeText(this, "Mã PIN phải có đúng 6 số", Toast.LENGTH_SHORT).show();
            return;
        }

        // Tạo request
        PinSetRequest request = new PinSetRequest(password, otp, newPin);

        Call<MessageResponse> call = apiService.setPin(authToken, request);
        call.enqueue(new Callback<MessageResponse>() {
            @Override
            public void onResponse(Call<MessageResponse> call, Response<MessageResponse> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(SetPinActivity.this, "Tạo mã PIN thành công!", Toast.LENGTH_LONG).show();
                    finish(); // Đóng màn hình này và quay lại HomeActivity
                } else {
                    // Lỗi (OTP sai, Mật khẩu sai, v.v.)
                    Toast.makeText(SetPinActivity.this, "Tạo PIN thất bại: Sai OTP hoặc Mật khẩu", Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<MessageResponse> call, Throwable t) {
                Toast.makeText(SetPinActivity.this, "Lỗi kết nối: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}