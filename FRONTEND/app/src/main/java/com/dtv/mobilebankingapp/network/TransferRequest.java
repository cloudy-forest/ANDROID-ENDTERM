package com.dtv.mobilebankingapp.network;

// Khớp vs schemas.TransactionCreate của FastAPI
public class TransferRequest {
    String receiver_account_number;
    int amount;
    String pin;

    public TransferRequest(String receiver_account_number, int amount, String pin) {
        this.receiver_account_number = receiver_account_number;
        this.amount = amount;
        this.pin = pin;
    }
}
