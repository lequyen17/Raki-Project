package com.example.payment_service.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.SortedMap;
import java.util.TreeMap;

@Slf4j
@Service
public class VnpayGatewayService {

    // Hardcoded credentials (sandbox)
    private static final String TMN_CODE = "0GE5WHDN";
    private static final String SECRET_KEY = "TLLSGXCHNSJQSWCMSXUSTJODJQXXZOIM";
    private static final String PAYMENT_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html";

    public String createPaymentUrl(long amount, String orderId, String ipaddr, String returnUrl) {
        ZoneId tz = ZoneId.of("Asia/Ho_Chi_Minh");
        ZonedDateTime now = ZonedDateTime.now(tz);
        ZonedDateTime expire = now.plusMinutes(60);
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");

        SortedMap<String, String> params = new TreeMap<>();
        params.put("vnp_Version", "2.1.0");
        params.put("vnp_Command", "pay");
        params.put("vnp_TmnCode", TMN_CODE);
        params.put("vnp_Amount", String.valueOf(amount * 100));
        params.put("vnp_CurrCode", "VND");
        params.put("vnp_TxnRef", orderId);
        params.put("vnp_OrderInfo", "Thanh toan don hang " + orderId);
        params.put("vnp_OrderType", "other");
        params.put("vnp_Locale", "vn");
        params.put("vnp_CreateDate", now.format(fmt));
        params.put("vnp_ExpireDate", expire.format(fmt));
        params.put("vnp_IpAddr", ipaddr != null ? ipaddr : "127.0.0.1");
        params.put("vnp_ReturnUrl", returnUrl != null ? returnUrl : "");

        StringBuilder queryBuilder = new StringBuilder();
        boolean first = true;
        for (Map.Entry<String, String> entry : params.entrySet()) {
            String value = entry.getValue();
            if (value != null && !value.isEmpty()) {
                if (!first) {
                    queryBuilder.append("&");
                }
                queryBuilder.append(entry.getKey())
                        .append("=")
                        .append(vnpayUrlEncode(value));
                first = false;
            }
        }

        String queryString = queryBuilder.toString();
        String secureHash = hmacSHA512(SECRET_KEY, queryString);

        return PAYMENT_URL + "?" + queryString + "&vnp_SecureHash=" + secureHash;
    }

    public boolean verifySignature(Map<String, String> params) {
        Map<String, String> data = new TreeMap<>(params);
        String vnpSecureHash = data.remove("vnp_SecureHash");
        data.remove("vnp_SecureHashType");

        if (vnpSecureHash == null || vnpSecureHash.isEmpty()) {
            return false;
        }

        StringBuilder hashDataBuilder = new StringBuilder();
        boolean first = true;
        for (Map.Entry<String, String> entry : new TreeMap<>(data).entrySet()) {
            String key = entry.getKey();
            String value = entry.getValue();
            if (key.startsWith("vnp_") && value != null && !value.isEmpty()) {
                if (!first) {
                    hashDataBuilder.append("&");
                }
                hashDataBuilder.append(key)
                        .append("=")
                        .append(vnpayUrlEncode(value));
                first = false;
            }
        }

        String hashValue = hmacSHA512(SECRET_KEY, hashDataBuilder.toString());
        return vnpSecureHash.equalsIgnoreCase(hashValue);
    }

  /**
   * Match Python urllib.parse.quote_plus used by the original Django gateway.
   */
  private String vnpayUrlEncode(String value) {
    return URLEncoder.encode(value, StandardCharsets.UTF_8);
  }

    private String hmacSHA512(String key, String data) {
        try {
            Mac hmac = Mac.getInstance("HmacSHA512");
            SecretKeySpec secretKey = new SecretKeySpec(key.getBytes(StandardCharsets.UTF_8), "HmacSHA512");
            hmac.init(secretKey);
            byte[] hash = hmac.doFinal(data.getBytes(StandardCharsets.UTF_8));

            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1)
                    hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate HMAC-SHA512", e);
        }
    }
}
