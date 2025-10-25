package com.dtv.mobilebankingapp;

import android.util.Log;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

import com.dtv.mobilebankingapp.network.Account;
import java.util.List;

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
    private TextView tvBalance;
    private ApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);

        sessionManager = new SessionManager(this);
        apiService = RetrofitClient.getApiService();

        tvUserInfo = findViewById(R.id.tvUserInfo);
        tvBalance = findViewById(R.id.tvBalance);
        Button btnLogout = findViewById(R.id.btnLogout);

        String token = sessionManager.getAuthToken();
        if (token == null) {
            goToLoginActivity();
            return;
        }

        String authToken = "Bearer " + token;

        // Gọi cả 2 API
        fetchUserInfo(authToken);
        fetchAccountInfo(authToken); // Gọi hàm mới

        btnLogout.setOnClickListener(v -> {
            sessionManager.clearAuthToken();
            goToLoginActivity();
        });
    }

    // --- HÀM 1: LẤY THÔNG TIN USER ---
    private void fetchUserInfo(String authToken) {
        // Bạn đã gõ 'String authToken' 2 lần
        // Bỏ dòng 'String authToken = "Bearer " + token;' ở đây

        Call<User> call = apiService.getMe(authToken);
        call.enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                if (response.isSuccessful() && response.body() != null) {
                    User user = response.body();
                    tvUserInfo.setText("Xin chào, " + user.getFullName());
                } else {
                    Log.e("GET_ME_ERROR", "Token không hợp lệ hoặc đã hết hạn.");
                    sessionManager.clearAuthToken();
                    goToLoginActivity();
                }
            }

            @Override
            public void onFailure(Call<User> call, Throwable t) {
                Log.e("GET_ME_FAILURE", "Lỗi kết nối: " + t.getMessage());
                tvUserInfo.setText("Lỗi tải dữ liệu.");
            }
        });
    }
    private void fetchAccountInfo(String authToken) {
        Call<List<Account>> call = apiService.getMyAccounts(authToken);
        call.enqueue(new Callback<List<Account>>() {
            @Override
            public void onResponse(Call<List<Account>> call, Response<List<Account>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<Account> accounts = response.body();

                    if (accounts.isEmpty()) {
                        tvBalance.setText("Số dư: N/A");
                    } else {
                        // Sửa lỗi gõ phím: "%, d" -> "%,d"
                        String formattedBalance = String.format("%,d VND", accounts.get(0).getBalance());
                        tvBalance.setText("Số dư: " + formattedBalance);
                    }
                } else {
                    Log.e("GET_ACCOUNTS_ERROR", "Lỗi khi lấy tài khoản");
                    tvBalance.setText("Số dư: Lỗi");
                }
            }

            @Override
            public void onFailure(Call<List<Account>> call, Throwable t) {
                Log.e("GET_ACCOUNTS_FAILURE", "Lỗi kết nối: " + t.getMessage());
                tvBalance.setText("Số dư: Lỗi kết nối");
            }
        });
    }

    // --- HÀM 3: ĐI TỚI MÀN HÌNH LOGIN ---
    private void goToLoginActivity() {
        Intent intent = new Intent(HomeActivity.this, LoginActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
}