package com.example.payment_service.service;

import com.example.payment_service.dto.request.CreatePaymentRequest;
import com.example.payment_service.dto.response.CallbackResult;
import com.example.payment_service.dto.response.CreatePaymentResponse;
import com.example.payment_service.dto.response.PaymentHistoryResponse;
import com.example.payment_service.entity.PaymentHistory;
import com.example.payment_service.entity.enums.PaymentProvider;
import com.example.payment_service.entity.enums.PaymentStatus;
import com.example.payment_service.repository.PaymentHistoryRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class PaymentService {

    private final PaymentHistoryRepository paymentHistoryRepository;
    private final VnpayGatewayService vnpayGatewayService;
    private final MomoGatewayService momoGatewayService;
    private final StripeGatewayService stripeGatewayService;

    // ========================
    // CREATE PAYMENT
    // ========================

    @Transactional
    public CreatePaymentResponse createPayment(CreatePaymentRequest request) {
        long amount = request.getAmount();
        if (amount < 10000) {
            throw new IllegalArgumentException("Minimum top up amount is 10,000 VND");
        }

        PaymentProvider provider = PaymentProvider.valueOf(request.getProvider().toUpperCase());

        // Step 1: Create PaymentHistory with temporary orderId
        PaymentHistory payment = PaymentHistory.builder()
                .userId(request.getUserId())
                .provider(provider)
                .amountVnd(amount)
                .coinReceived((int) amount) // 1:1 VND to coin
                .status(PaymentStatus.PENDING)
                .orderId("temp_" + UUID.randomUUID().toString().replace("-", "").substring(0, 8))
                .build();
        payment = paymentHistoryRepository.save(payment);

        // Step 2: Generate real orderId with payment ID (same format as original Python code)
        String orderId = payment.getId() + "_" + UUID.randomUUID().toString().replace("-", "").substring(0, 8);
        payment.setOrderId(orderId);
        payment = paymentHistoryRepository.save(payment);

        // Step 3: Call the appropriate gateway
        try {
            switch (provider) {
                case VNPAY -> {
                    String payUrl = vnpayGatewayService.createPaymentUrl(
                            amount, orderId,
                            request.getIpaddr(),
                            request.getReturnUrl()
                    );
                    return CreatePaymentResponse.builder()
                            .payUrl(payUrl)
                            .paymentId(payment.getId())
                            .orderId(orderId)
                            .build();
                }
                case MOMO -> {
                    String payUrl = momoGatewayService.createPaymentUrl(
                            amount, orderId,
                            request.getRedirectUrl(),
                            request.getIpnUrl()
                    );
                    return CreatePaymentResponse.builder()
                            .payUrl(payUrl)
                            .paymentId(payment.getId())
                            .orderId(orderId)
                            .build();
                }
                case STRIPE -> {
                    Map<String, String> result = stripeGatewayService.createCheckoutSession(
                            amount, orderId,
                            request.getSuccessUrl(),
                            request.getCancelUrl(),
                            request.getUserEmail()
                    );
                    return CreatePaymentResponse.builder()
                            .payUrl(result.get("pay_url"))
                            .paymentId(payment.getId())
                            .orderId(orderId)
                            .sessionId(result.get("session_id"))
                            .build();
                }
                default -> throw new IllegalArgumentException("Unsupported provider: " + provider);
            }
        } catch (Exception e) {
            log.error("Payment creation failed for provider {}: {}", provider, e.getMessage());
            throw new RuntimeException("Payment creation failed: " + e.getMessage(), e);
        }
    }

    // ========================
    // VNPAY IPN
    // ========================

    @Transactional
    public CallbackResult processVnpayIpn(Map<String, String> params) {
        if (params == null || params.isEmpty()) {
            return CallbackResult.builder()
                    .success(false).rspCode("99").message("Invalid request").build();
        }

        if (!vnpayGatewayService.verifySignature(params)) {
            return CallbackResult.builder()
                    .success(false).rspCode("97").message("Invalid Signature").build();
        }

        String orderId = params.get("vnp_TxnRef");
        String vnpResponseCode = params.get("vnp_ResponseCode");

        Optional<PaymentHistory> paymentOpt = paymentHistoryRepository.findByOrderId(orderId);
        if (paymentOpt.isEmpty()) {
            return CallbackResult.builder()
                    .success(false).rspCode("01").message("Order not found").build();
        }

        PaymentHistory payment = paymentOpt.get();

        if (payment.getStatus() != PaymentStatus.PENDING) {
            if (payment.getStatus() == PaymentStatus.COMPLETED && "00".equals(vnpResponseCode)) {
                return CallbackResult.builder()
                        .success(false)
                        .rspCode("00")
                        .message("Confirm Success")
                        .build();
            }
            return CallbackResult.builder()
                    .success(false).rspCode("02").message("Order Already Update").build();
        }

        long vnpAmount = Long.parseLong(params.getOrDefault("vnp_Amount", "0"));
        if (vnpAmount != payment.getAmountVnd() * 100) {
            return CallbackResult.builder()
                    .success(false).rspCode("04").message("invalid amount").build();
        }

        if ("00".equals(vnpResponseCode)) {
            payment.setStatus(PaymentStatus.COMPLETED);
            payment.setProviderTransactionId(params.get("vnp_TransactionNo"));
            paymentHistoryRepository.save(payment);

            return CallbackResult.builder()
                    .success(true)
                    .userId(payment.getUserId())
                    .coinReceived(payment.getCoinReceived())
                    .rspCode("00")
                    .message("Confirm Success")
                    .build();
        } else {
            payment.setStatus(PaymentStatus.FAILED);
            paymentHistoryRepository.save(payment);

            return CallbackResult.builder()
                    .success(false)
                    .rspCode(vnpResponseCode)
                    .message("Payment Failed")
                    .build();
        }
    }

    // ========================
    // VNPAY VERIFY RESULT (for result page)
    // ========================

    public CallbackResult verifyVnpayResult(Map<String, String> params) {
        String vnpResponseCode = params.get("vnp_ResponseCode");
        String vnpTxnRef = params.get("vnp_TxnRef");
        String vnpSecureHash = params.get("vnp_SecureHash");

        if (vnpResponseCode != null && vnpTxnRef != null && vnpSecureHash != null) {
            boolean valid = vnpayGatewayService.verifySignature(params);
            boolean isSuccess = valid && "00".equals(vnpResponseCode);
            return CallbackResult.builder()
                    .success(isSuccess)
                    .message(valid ? (isSuccess ? "valid" : "payment_failed") : "invalid_signature")
                    .build();
        }

        return CallbackResult.builder()
                .success(false)
                .message("missing_params")
                .build();
    }

    // ========================
    // MOMO CALLBACK
    // ========================

    @Transactional
    public CallbackResult processMomoCallback(String orderId, String resultCode) {
        if (orderId == null || orderId.isEmpty()) {
            return CallbackResult.builder()
                    .success(false).message("Missing orderId").build();
        }

        if ("0".equals(resultCode)) {
            Optional<PaymentHistory> paymentOpt = paymentHistoryRepository.findByOrderId(orderId);
            if (paymentOpt.isEmpty()) {
                return CallbackResult.builder()
                        .success(false).message("Payment not found").build();
            }

            PaymentHistory payment = paymentOpt.get();
            if (payment.getStatus() == PaymentStatus.PENDING) {
                payment.setStatus(PaymentStatus.COMPLETED);
                paymentHistoryRepository.save(payment);

                return CallbackResult.builder()
                        .success(true)
                        .userId(payment.getUserId())
                        .coinReceived(payment.getCoinReceived())
                        .message("Success")
                        .build();
            }

            return CallbackResult.builder()
                    .success(false).message("Already processed").build();
        } else {
            log.warn("MoMo payment failed or canceled for order {}", orderId);
            return CallbackResult.builder()
                    .success(false).message("Payment failed from MoMo").build();
        }
    }

    // ========================
    // STRIPE WEBHOOK
    // ========================

    @Transactional
    public CallbackResult processStripeWebhook(String payload, String sigHeader) {
        String webhookSecret = stripeGatewayService.getWebhookSecret();

        if (webhookSecret != null && !webhookSecret.isEmpty()) {
            if (!stripeGatewayService.verifyWebhook(payload, sigHeader)) {
                return CallbackResult.builder()
                        .success(false).message("Signature verification failed").build();
            }
        }

        try {
            ObjectMapper mapper = new ObjectMapper();
            Map<String, Object> eventDict = mapper.readValue(payload, new TypeReference<>() {});

            String eventType = (String) eventDict.get("type");
            if ("checkout.session.completed".equals(eventType)) {
                @SuppressWarnings("unchecked")
                Map<String, Object> dataObj = (Map<String, Object>) eventDict.getOrDefault("data", Map.of());
                @SuppressWarnings("unchecked")
                Map<String, Object> sessionData = (Map<String, Object>) dataObj.getOrDefault("object", Map.of());
                @SuppressWarnings("unchecked")
                Map<String, String> metadata = (Map<String, String>) sessionData.getOrDefault("metadata", Map.of());

                String orderId = metadata.get("order_id");
                if (orderId == null || orderId.isEmpty()) {
                    return CallbackResult.builder()
                            .success(false).message("Missing order_id").build();
                }

                Optional<PaymentHistory> paymentOpt = paymentHistoryRepository.findByOrderId(orderId);
                if (paymentOpt.isEmpty()) {
                    return CallbackResult.builder()
                            .success(false).message("Payment not found").build();
                }

                PaymentHistory payment = paymentOpt.get();
                if (payment.getStatus() == PaymentStatus.PENDING) {
                    payment.setStatus(PaymentStatus.COMPLETED);
                    paymentHistoryRepository.save(payment);

                    return CallbackResult.builder()
                            .success(true)
                            .userId(payment.getUserId())
                            .coinReceived(payment.getCoinReceived())
                            .message("Success")
                            .build();
                }
            }

            return CallbackResult.builder()
                    .success(false).message("Unhandled event type").build();
        } catch (Exception e) {
            log.error("Error processing Stripe webhook: {}", e.getMessage());
            return CallbackResult.builder()
                    .success(false).message("Failed to parse webhook: " + e.getMessage()).build();
        }
    }

    // ========================
    // PAYMENT HISTORIES
    // ========================

    public List<PaymentHistoryResponse> getPaymentHistories(Long userId) {
        return paymentHistoryRepository.findByUserIdOrderByCreatedAtDesc(userId).stream()
                .map(p -> PaymentHistoryResponse.builder()
                        .id(p.getId())
                        .amountVnd(String.valueOf(p.getAmountVnd()))
                        .coinReceived(p.getCoinReceived())
                        .provider(p.getProvider().name())
                        .status(p.getStatus().name().toLowerCase())
                        .createdAt(p.getCreatedAt())
                        .build())
                .collect(Collectors.toList());
    }
}
