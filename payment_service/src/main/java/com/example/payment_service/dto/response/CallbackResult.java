package com.example.payment_service.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CallbackResult {
    private boolean success;         // Whether coin should be added
    private Long userId;
    private Integer coinReceived;
    private String message;
    private String rspCode;          // VNPay specific response code
    private Map<String, String> gatewayResponse;  // Raw response for gateway
}
