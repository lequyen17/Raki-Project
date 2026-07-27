package com.example.payment_service.repository;

import com.example.payment_service.entity.PaymentHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PaymentHistoryRepository extends JpaRepository<PaymentHistory, Long> {

    Optional<PaymentHistory> findByOrderId(String orderId);

    List<PaymentHistory> findByUserIdOrderByCreatedAtDesc(Long userId);
}
