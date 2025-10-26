package com.dtv.mobilebankingapp;

import android.util.Log;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import android.widget.EditText;
import android.widget.Toast;
import com.dtv.mobilebankingapp.network.Account;
import java.util.List;

import com.dtv.mobilebankingapp.network.SessionManager;
import com.dtv.mobilebankingapp.network.ApiService;
import com.dtv.mobilebankingapp.network.RetrofitClient;
import com.dtv.mobilebankingapp.network.User;
import com.dtv.mobilebankingapp.network.TransferRequest;
import com.dtv.mobilebankingapp.network.TransactionResponse;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class HomeActivity extends AppCompatActivity {

    private SessionManager sessionManager;
    private TextView tvUserInfo;
    private TextView tvBalance;
    private ApiService apiService;
    private EditText etReceiverAccount;
    private EditText etAmount;
    private Button btnTransfer;
    private String authToken; // Lưu token để dùng lại

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);

        sessionManager = new SessionManager(this);
        apiService = RetrofitClient.getApiService();

        tvUserInfo = findViewById(R.id.tvUserInfo);
        tvBalance = findViewById(R.id.tvBalance);
        Button btnLogout = findViewById(R.id.btnLogout);

        etReceiverAccount = findViewById(R.id.etReceiverAccount);
        etAmount = findViewById(R.id.etAmount);
        btnTransfer = findViewById(R.id.btnTransfer);

        String token = sessionManager.getAuthToken();
        if (token == null) {
            goToLoginActivity();
            return;
        }

        // Lưu token để dùng cho tất cả API
        authToken = "Bearer " + token;

        // Gọi cả 2 API
        fetchUserInfo(authToken);
        fetchAccountInfo(authToken); // Gọi hàm mới

        btnLogout.setOnClickListener(v -> {
            sessionManager.clearAuthToken();
            goToLoginActivity();
        });

        // Gán sự kiện cho nút chuyển tiền
        btnTransfer.setOnClickListener(v -> {
            handleTransfer();
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

    private void handleTransfer() {
        String receiverAccount = etReceiverAccount.getText().toString();
        String amountString = etAmount.getText().toString();

        // 1. Kiểm tra input
        if (receiverAccount.isEmpty() || amountString.isEmpty()) {
            Toast.makeText(this, "Vui lòng nhập đủ thông tin", Toast.LENGTH_SHORT).show();
            return;
        }

        int amount;
        try {
            amount = Integer.parseInt(amountString);
        } catch (NumberFormatException e) {
            Toast.makeText(this, "Số tiền không hợp lệ", Toast.LENGTH_SHORT).show();
            return;
        }

        if (amount <= 0) {
            Toast.makeText(this, "số tiền phải lớn hơn 0", Toast.LENGTH_SHORT).show();
            return;
        }

        // 2. Tạo Request Body
        TransferRequest request = new TransferRequest(receiverAccount, amount);

        // 3. Gọi API (dùng lại authToken đã lưu)
        Call<TransactionResponse> call = apiService.performTransfer(authToken, request);
        call.enqueue(new Callback<TransactionResponse>() {
            @Override
            public void onResponse(Call<TransactionResponse> call, Response<TransactionResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    // THÀNH CÔNG
                    Toast.makeText(HomeActivity.this, "Chuyển tiền thành công !", Toast.LENGTH_SHORT).show();

                    // Xóa input
                    etReceiverAccount.setText("");
                    etAmount.setText("");

                    // QUAN TRỌNG: Tải lại số dư mới
                    fetchAccountInfo(authToken);

                } else {
                    // THẤT BẠI (không đủ tiền, STK sai)\
                    // (đọc lỗi chi tiết từ response.errorBody())
                    Toast.makeText(HomeActivity.this, "Chuyển tiền thất bại (Số tài khoản sai hoặc không đủ số dư)", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<TransactionResponse> call, Throwable t) {
                Toast.makeText(HomeActivity.this, "Lỗi kết nối" + t.getMessage(), Toast.LENGTH_SHORT).show();
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