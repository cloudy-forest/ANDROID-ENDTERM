package com.dtv.mobilebankingapp;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

import com.dtv.mobilebankingapp.network.SessionManager;

public class HomeActivity extends AppCompatActivity {

   private SessionManager sessionManager;

   @Override
    protected void onCreate(Bundle savedInstanceState) {
       super.onCreate(savedInstanceState);
       setContentView(R.layout.activity_home);

       sessionManager = new SessionManager(this);
       TextView tvUserInfo = findViewById(R.id.tvUserInfo);
       Button btnLogout = findViewById(R.id.btnLogout);

       // TODO: Gọi API /api/users/me để lấy thông tin user và hiển thị
       // tvUserInfo.setText("Xin chào, " + user.getFullName());

       btnLogout.setOnClickListener(v -> {
           // Xóa token
           sessionManager.clearAuthToken();

           // Quay về màn hình Login
           Intent intent = new Intent(HomeActivity.this, LoginActivity.class);
           // Cờ này xóa hết các Activity cũ, đảm bảo user không "back" lại được
           intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
           startActivity(intent);
       });
   }
}