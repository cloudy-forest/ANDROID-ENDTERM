package com.dtv.mobilebankingapp; // Đảm bảo tên package này đúng với của bạn
import android.widget.Toast;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.util.Log;

import androidx.appcompat.app.AppCompatActivity;

import com.dtv.mobilebankingapp.network.LoginRequest;
import com.dtv.mobilebankingapp.network.LoginResponse;
import com.dtv.mobilebankingapp.network.RetrofitClient;
import com.dtv.mobilebankingapp.network.ApiService;
import com.dtv.mobilebankingapp.network.LoginRequest;
import com.dtv.mobilebankingapp.network.LoginResponse;
import com.dtv.mobilebankingapp.network.RetrofitClient;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Kết nối với file layout activity_login.xml
        setContentView(R.layout.activity_login);

        // Ánh xạ các view
        EditText etUsername = findViewById(R.id.etUsername);
        EditText etPassword = findViewById(R.id.etPassword);
        Button btnLogin = findViewById(R.id.btnLogin);

        // Lấy service API từ RetrofitClient
        ApiService apiService = RetrofitClient.getApiService();
        // Gán sự kiện click cho nút Login
        btnLogin.setOnClickListener(v -> {
            String username = etUsername.getText().toString();
            String password = etPassword.getText().toString();

            if (username.isEmpty() || password.isEmpty()) {
                Toast.makeText(LoginActivity.this, "Vui lòng nhập đủ thông tin", Toast.LENGTH_SHORT).show();
                return;
            }

            // 1. Tạo đối tượng request
            LoginRequest loginRequest = new LoginRequest(username, password);

            // 2. Gọi API (bất đồng bộ)
            Call<LoginResponse> call = apiService.login(loginRequest);
            call.enqueue(new Callback<LoginResponse>() {
                // 3. Xử lí khi API trả về KẾT QUẢ (thành công hoặc thất bại)
                @Override
                public void onResponse(Call<LoginResponse> call, Response<LoginResponse> response) {
                    if (response.isSuccessful()) {
                        // Thành công (HTTP Code 200-299)
                        LoginResponse loginResponse = response.body();
                        String token = loginResponse.getToken();

                        // HIỂN THỊ THÀNH CÔNG
                        Toast.makeText(LoginActivity.this, "Đăng nhập thành công !", Toast.LENGTH_SHORT).show();
                        Log.d("LOGIN_SUCCESS", "Token: " + token);

                        // TODO: Lưu token này lại (dùng SharedPreferences)
                        // TODO: Chuyển sang màn hình HomeActivity
                    } else {
                        // Thất bai (HTTP Code 401, 404, 500...)
                        // (VD: Sai mật khẩu)
                        Toast.makeText(LoginActivity.this, "Sai tên đăng nhập hoặc mật khẩu", Toast.LENGTH_SHORT).show();
                    }
                }

                // 4. Xử lí khi API GẶP LỖI (mất mạng, không kết nối được server)
                @Override
                public void onFailure(Call<LoginResponse> call, Throwable t) {
                    Toast.makeText(LoginActivity.this, "Lỗi kết nối: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    Log.e("LOGIN_FAILURE", t.getMessage());
                }
            });
        });
    }
}