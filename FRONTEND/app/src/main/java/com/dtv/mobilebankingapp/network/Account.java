package com.dtv.mobilebankingapp.network;

public class Account {
    private int id;
    private String account_number;
    private int balance;
    private int owner_id;

    // Getters
    public String getAccountNumber() {
        return account_number;
    }

    public int getBalance() {
        return balance;
    }
}
