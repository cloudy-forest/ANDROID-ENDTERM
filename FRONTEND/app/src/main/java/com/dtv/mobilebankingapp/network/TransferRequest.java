package com.dtv.mobilebankingapp.network;

// Khớp vs schemas.TransactionCreate của FastAPI
public class TransferRequest {
    String receiver_account_number;
    int amount;

    public TransferRequest(String receiver_account_number, int amount) {
        this.receiver_account_number = receiver_account_number;
        this.amount = amount;
    }
}
