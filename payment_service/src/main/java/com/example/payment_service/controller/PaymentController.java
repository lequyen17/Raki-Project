package com.example.payment_service.controller;

import com.example.payment_service.dto.request.CreatePaymentRequest;
import com.example.payment_service.dto.response.ApiResponse;
import com.example.payment_service.dto.response.CallbackResult;
import com.example.payment_service.dto.response.CreatePaymentResponse;
import com.example.payment_service.dto.response.PaymentHistoryResponse;
import com.example.payment_service.service.PaymentService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/payment")
@RequiredArgsConstructor
public class PaymentController {

    private final PaymentService paymentService;

    /**
     * Create a new payment (called by Raki backend)
     */
    @PostMapping("/create")
    public ResponseEntity<ApiResponse<CreatePaymentResponse>> createPayment(
            @RequestBody CreatePaymentRequest request) {
        try {
            CreatePaymentResponse response = paymentService.createPayment(request);
            return ResponseEntity.ok(ApiResponse.ok(response));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(ApiResponse.error(e.getMessage()));
        } catch (Exception e) {
            log.error("Create payment error: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Payment creation failed: " + e.getMessage()));
        }
    }

    /**
     * Process VNPay IPN callback (forwarded by Raki backend)
     */
    @PostMapping("/vnpay/ipn")
    public ResponseEntity<CallbackResult> processVnpayIpn(@RequestBody Map<String, String> params) {
        log.info("VNPay IPN received: {}", params);
        CallbackResult result = paymentService.processVnpayIpn(params);
        return ResponseEntity.ok(result);
    }

    /**
     * Verify VNPay result page params (forwarded by Raki backend)
     */
    @PostMapping("/vnpay/verify-result")
    public ResponseEntity<CallbackResult> verifyVnpayResult(@RequestBody Map<String, String> params) {
        CallbackResult result = paymentService.verifyVnpayResult(params);
        return ResponseEntity.ok(result);
    }

    /**
     * Process MoMo callback (forwarded by Raki backend)
     */
    @PostMapping("/momo/callback")
    public ResponseEntity<CallbackResult> processMomoCallback(@RequestBody Map<String, String> params) {
        log.info("MoMo callback received: {}", params);
        String orderId = params.get("orderId");
        String resultCode = params.get("resultCode");
        CallbackResult result = paymentService.processMomoCallback(orderId, resultCode);
        return ResponseEntity.ok(result);
    }

    /**
     * Process Stripe webhook (forwarded by Raki backend)
     */
    @PostMapping("/stripe/webhook")
    public ResponseEntity<CallbackResult> processStripeWebhook(@RequestBody Map<String, String> params) {
        log.info("Stripe webhook received");
        String payload = params.get("payload");
        String sigHeader = params.get("sigHeader");
        CallbackResult result = paymentService.processStripeWebhook(payload, sigHeader);
        return ResponseEntity.ok(result);
    }

    /**
     * Get payment histories for a user (called by Raki backend)
     */
    @GetMapping("/history/{userId}")
    public ResponseEntity<ApiResponse<List<PaymentHistoryResponse>>> getPaymentHistories(
            @PathVariable Long userId) {
        List<PaymentHistoryResponse> histories = paymentService.getPaymentHistories(userId);
        return ResponseEntity.ok(ApiResponse.ok(histories));
    }
}
