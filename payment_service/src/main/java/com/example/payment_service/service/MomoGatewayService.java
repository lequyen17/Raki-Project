package com.example.payment_service.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class MomoGatewayService {

    // Hardcoded credentials (sandbox)
    private static final String PARTNER_CODE = "MOMO";
    private static final String ACCESS_KEY = "F8BBA842ECF85";
    private static final String SECRET_KEY = "K951B6PE1waDMi640xX08PD3vg6EkVlz";
    private static final String ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/create";

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public String createPaymentUrl(long amount, String orderId, String redirectUrl, String ipnUrl) {
        String requestType = "payWithMethod";
        String orderInfo = "pay with MoMo";
        String extraData = "";
        String requestId = UUID.randomUUID().toString();

        String rawSignature = String.format(
                "accessKey=%s&amount=%d&extraData=%s&ipnUrl=%s&orderId=%s&orderInfo=%s&partnerCode=%s&redirectUrl=%s&requestId=%s&requestType=%s",
                ACCESS_KEY, amount, extraData,
                ipnUrl != null ? ipnUrl : "",
                orderId, orderInfo, PARTNER_CODE,
                redirectUrl != null ? redirectUrl : "",
                requestId, requestType
        );

        String signature = hmacSHA256(SECRET_KEY, rawSignature);

        Map<String, Object> requestBody = new LinkedHashMap<>();
        requestBody.put("partnerCode", PARTNER_CODE);
        requestBody.put("orderId", orderId);
        requestBody.put("partnerName", "MoMo Payment");
        requestBody.put("storeId", "Test Store");
        requestBody.put("ipnUrl", ipnUrl != null ? ipnUrl : "");
        requestBody.put("amount", String.valueOf(amount));
        requestBody.put("lang", "vi");
        requestBody.put("requestType", requestType);
        requestBody.put("redirectUrl", redirectUrl != null ? redirectUrl : "");
        requestBody.put("autoCapture", true);
        requestBody.put("orderInfo", orderInfo);
        requestBody.put("requestId", requestId);
        requestBody.put("extraData", extraData);
        requestBody.put("signature", signature);
        requestBody.put("orderGroupId", "");

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            String jsonBody = objectMapper.writeValueAsString(requestBody);
            HttpEntity<String> entity = new HttpEntity<>(jsonBody, headers);

            ResponseEntity<Map> response = restTemplate.exchange(
                    ENDPOINT, HttpMethod.POST, entity, Map.class
            );

            Map<String, Object> responseBody = response.getBody();
            if (responseBody != null) {
                return (String) responseBody.get("payUrl");
            }
            throw new RuntimeException("Empty response from MoMo");
        } catch (Exception e) {
            log.error("MoMo payment creation failed: {}", e.getMessage());
            throw new RuntimeException("MoMo payment creation failed: " + e.getMessage(), e);
        }
    }

    private String hmacSHA256(String key, String data) {
        try {
            Mac hmac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKey = new SecretKeySpec(key.getBytes(StandardCharsets.US_ASCII), "HmacSHA256");
            hmac.init(secretKey);
            byte[] hash = hmac.doFinal(data.getBytes(StandardCharsets.US_ASCII));

            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate HMAC-SHA256", e);
        }
    }
}
