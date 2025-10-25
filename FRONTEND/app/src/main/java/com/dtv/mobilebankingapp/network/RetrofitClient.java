package com.dtv.mobilebankingapp.network;

import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
public class RetrofitClient {
    // Quan trọng: đây là IP của máy tính ( localhost)
    // khi nhìn từ mmays ảo Android

    private static final String BASE_URL = "http://10.0.2.2:8080";

    private static Retrofit retrofit = null;
    private static ApiService apiService = null;

    // Hàm private constructor để ngăn tạo nhiều instance
    private RetrofitClient() {}

    // Hàm để lấy instance Retrofit
    public static Retrofit getRetrofitInstance() {
        if (retrofit == null) {
            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create()) // Dùng Gson
                    .build();
        }
        return retrofit;
    }

    // Hàm tiện ích để lấy luôn ApiService
    public static ApiService getApiService() {
        if (apiService == null) {
            apiService = getRetrofitInstance().create(ApiService.class);
        }
        return apiService;
    }

}
