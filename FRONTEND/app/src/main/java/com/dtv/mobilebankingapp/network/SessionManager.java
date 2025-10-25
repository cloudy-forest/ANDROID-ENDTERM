package com.dtv.mobilebankingapp.network;

import android.content.Context;
import android.content.SharedPreferences;

public class SessionManager {
    private static final String PREF_NAME = "MobileBankingPref";
    private static final String KEY_TOKEN = "api_token";

    private SharedPreferences sharedPreferences;
    private SharedPreferences.Editor editor;
    private Context context;

    public SessionManager(Context context) {
        this.context = context;
        sharedPreferences = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        editor = sharedPreferences.edit();
    }

    // Lưu token khi đăng nhập
    public void saveAuthToken(String token) {
        editor.putString(KEY_TOKEN, token);
        editor.commit(); // Lưu lại
    }

    // Lấy token để sử dụng
    public String getAuthToken() {
        return sharedPreferences.getString(KEY_TOKEN, null);
    }

    // Xóa token khi đăng xuất
    public void clearAuthToken() {
        editor.remove(KEY_TOKEN);
        editor.commit();
    }
}