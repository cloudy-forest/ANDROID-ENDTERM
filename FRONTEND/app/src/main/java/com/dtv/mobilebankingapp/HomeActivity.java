package com.dtv.mobilebankingapp;

import android.util.Log;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

import com.dtv.mobilebankingapp.network.SessionManager;
import com.dtv.mobilebankingapp.network.ApiService;
import com.dtv.mobilebankingapp.network.RetrofitClient;
import com.dtv.mobilebankingapp.network.User;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class HomeActivity extends AppCompatActivity {

   private SessionManager sessionManager;
   private TextView tvUserInfo;

   @Override
    protected void onCreate(Bundle savedInstanceState) {
       super.onCreate(savedInstanceState);
       setContentView(R.layout.activity_home);

       sessionManager = new SessionManager(this);
       tvUserInfo = findViewById(R.id.tvUserInfo);
       Button btnLogout = findViewById(R.id.btnLogout);

       // Lấy token đã lưu
       String token = sessionManager.getAuthToken();
       if (token == null) {
           // Nếu không có token, đá về login (đề phòng)
           goToLoginActivity();
           return;
       }

       // Gọi API để lấy thông tin user
       fetchUserInfo(token);

       btnLogout.setOnClickListener(v -> {
           // Xóa token
           sessionManager.clearAuthToken();
           goToLoginActivity();
       });
   }

   private void fetchUserInfo(String token) {
       // Lấy ApiService
       ApiService apiService = RetrofitClient.getApiService();

       // Tạo lời gọi API
       // Quan trọng: Phải thêm "Bearer " (có dấu cách)
       // Đây là tiêu chuẩn của JWT
       String authToken = "Bearer " + token;

       Call<User> call = apiService.getMe(authToken);
       call.enqueue(new Callback<User>() {
           @Override
           public void onResponse(Call<User> call, Response<User> response) {
               if (response.isSuccessful() && response.body() != null) {
                   // Thành công, lấy user
                   User user = response.body();

                   // Cập nhật TextView
                   tvUserInfo.setText("Xin chào, " + user.getFullName());
               } else {
                   // Lỗi (token hết hạn)
                   Log.e("GET_ME_ERROR", "Token không hợp lệ hoặc đã hết hạn.");
                   // Xóa token hỏng và quay về Login
                   sessionManager.clearAuthToken();
                   goToLoginActivity();
               }
           }

           @Override
           public void onFailure(Call<User> call, Throwable t) {
                // Lỗi kết nối
               Log.e("GET_ME_FAILURE", "Lỗi kết nối: " + t.getMessage());
               tvUserInfo.setText("Lỗi tải dữ liệu.");
           }
       });
   }

   // Hàm tiện ích để quay về Login
    private void goToLoginActivity() {
       Intent intent = new Intent(HomeActivity.this, LoginActivity.class);
       intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
       startActivity(intent);
       finish();
    }
}