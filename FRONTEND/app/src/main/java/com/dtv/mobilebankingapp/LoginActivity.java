package com.dtv.mobilebankingapp; // Đảm bảo tên package này đúng với của bạn
import android.widget.Toast;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;

import androidx.appcompat.app.AppCompatActivity;

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

        // Gán sự kiện click cho nút Login
        btnLogin.setOnClickListener(v -> {
            String username = etUsername.getText().toString();
            String password = etPassword.getText().toString();

            if (username.isEmpty() || password.isEmpty()) {
                Toast.makeText(LoginActivity.this, "Vui lòng nhập đủ thông tin", Toast.LENGTH_SHORT).show();
            } else {
                // TODO: Gọi API Login
                Toast.makeText(LoginActivity.this, "Username: " + username, Toast.LENGTH_SHORT).show();
            }
        });
    }
}