package com.example.payment_service.service;

import com.stripe.Stripe;
import com.stripe.model.checkout.Session;
import com.stripe.net.Webhook;
import com.stripe.param.checkout.SessionCreateParams;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
public class StripeGatewayService {

    // Hardcoded credentials (sandbox)
    private static final String SECRET_KEY = "sk_test_51TkpnARuDgugaDRen1N64IetOEcfhioMyHcbIZfVHjmHbP64mhkriEApk1bMiBWn1RvCNlF43Z4KiZmWl5qBxT0Z00gRqfMhIe";
    private static final String WEBHOOK_SECRET = "whsec_jeYVUSC8RMR865OWOiWmqSKTVF6UZWnU";

    @PostConstruct
    public void init() {
        Stripe.apiKey = SECRET_KEY;
    }

    public Map<String, String> createCheckoutSession(long amount, String orderId,
                                                      String successUrl, String cancelUrl,
                                                      String userEmail) {
        try {
            SessionCreateParams.Builder paramsBuilder = SessionCreateParams.builder()
                    .addPaymentMethodType(SessionCreateParams.PaymentMethodType.CARD)
                    .addLineItem(
                            SessionCreateParams.LineItem.builder()
                                    .setPriceData(
                                            SessionCreateParams.LineItem.PriceData.builder()
                                                    .setCurrency("vnd")
                                                    .setProductData(
                                                            SessionCreateParams.LineItem.PriceData.ProductData.builder()
                                                                    .setName(String.format("Raki Coin Top-up - %,d VND", amount))
                                                                    .setDescription("Order " + orderId)
                                                                    .build()
                                                    )
                                                    .setUnitAmount(amount)
                                                    .build()
                                    )
                                    .setQuantity(1L)
                                    .build()
                    )
                    .setMode(SessionCreateParams.Mode.PAYMENT)
                    .setSuccessUrl(successUrl)
                    .setCancelUrl(cancelUrl)
                    .putMetadata("order_id", orderId);

            if (userEmail != null && !userEmail.isEmpty()) {
                paramsBuilder.setCustomerEmail(userEmail);
            }

            Session session = Session.create(paramsBuilder.build());

            Map<String, String> result = new HashMap<>();
            result.put("pay_url", session.getUrl());
            result.put("session_id", session.getId());
            return result;
        } catch (Exception e) {
            log.error("Stripe checkout session creation failed: {}", e.getMessage());
            throw new RuntimeException("Stripe payment creation failed: " + e.getMessage(), e);
        }
    }

    public boolean verifyWebhook(String payload, String sigHeader) {
        if (WEBHOOK_SECRET == null || WEBHOOK_SECRET.isEmpty()) {
            return true;
        }
        try {
            Webhook.constructEvent(payload, sigHeader, WEBHOOK_SECRET);
            return true;
        } catch (Exception e) {
            log.error("Stripe webhook verification failed: {}", e.getMessage());
            return false;
        }
    }

    public String getWebhookSecret() {
        return WEBHOOK_SECRET;
    }
}
