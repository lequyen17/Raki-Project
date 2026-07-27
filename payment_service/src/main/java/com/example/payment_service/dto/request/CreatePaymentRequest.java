package com.example.payment_service.dto.request;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreatePaymentRequest {
    private Long userId;
    private Long amount;
    private String provider;   // VNPAY, MOMO, STRIPE

    // VNPay specific
    private String ipaddr;
    private String returnUrl;

    // MoMo specific
    private String redirectUrl;
    private String ipnUrl;

    // Stripe specific
    private String successUrl;
    private String cancelUrl;
    private String userEmail;
}
