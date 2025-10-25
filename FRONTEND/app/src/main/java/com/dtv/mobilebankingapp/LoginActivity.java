package com.dtv.mobilebankingapp; // Đảm bảo tên package này đúng với của bạn
import android.widget.Toast;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.util.Log;
import android.content.Intent;

import androidx.appcompat.app.AppCompatActivity;

import com.dtv.mobilebankingapp.network.LoginRequest;
import com.dtv.mobilebankingapp.network.LoginResponse;
import com.dtv.mobilebankingapp.network.RetrofitClient;
import com.dtv.mobilebankingapp.network.ApiService;
import com.dtv.mobilebankingapp.network.LoginRequest;
import com.dtv.mobilebankingapp.network.LoginResponse;
import com.dtv.mobilebankingapp.network.RetrofitClient;
import com.dtv.mobilebankingapp.network.SessionManager;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginActivity extends AppCompatActivity {

    private SessionManager sessionManager;
    private ApiService apiService;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 1. Kiểm tra đăng nhập
        sessionManager = new SessionManager(this);
        if (sessionManager.getAuthToken() != null) {
            // Nếu đã có token, vào Home luôn, không cần đăng nhập nữa
            goToHomeActivity();
            return; // Dừng hàm onCreate ở đây
        }

        // 2. Nếu chưa đăng nhập, hiển thị layout
        setContentView(R.layout.activity_login);

        // Ánh xạ các view
        EditText etUsername = findViewById(R.id.etUsername);
        EditText etPassword = findViewById(R.id.etPassword);
        Button btnLogin = findViewById(R.id.btnLogin);

        // Lấy service API từ RetrofitClient
        apiService = RetrofitClient.getApiService();
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

                        // 3. lưu token và chuyển màn hình
                        sessionManager.saveAuthToken(token);
                        Toast.makeText(LoginActivity.this, "Đăng nhập thành công !", Toast.LENGTH_SHORT).show();
                        Log.d("LOGIN_SUCCESS", "Token: " + token);

                        // Chuyển sang màn hình HomeActivity
                        goToHomeActivity();
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

    // hàm tiện ích để chuyển màn hình
    private void goToHomeActivity() {
        Intent intent = new Intent(LoginActivity.this, HomeActivity.class);
        // Xóa các Activity cũ, user không "back" lại màn hình login được
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish(); // Đóng LoginActivity
    }
}