# Hướng Dẫn Triển Khai Kubernetes Cho Raki Project

Thư mục `k8s/` chứa toàn bộ các file manifests đã được chuẩn hóa để triển khai hệ thống **Raki Project** lên cụm Kubernetes (Local như Minikube, Kind, k3s, Docker Desktop hoặc Cloud như GKE, EKS, AKS).

---

## 1. Cấu Trúc Thư Mục

```
k8s/
├── namespace.yaml                  # Tạo Namespace 'raki'
├── kustomization.yaml              # Kustomize manifest tổng hợp
│
├── postgres/                       # PostgreSQL DB cho Django backend (db / postgres)
├── redis/                          # In-memory Redis Cache & Session
├── rabbitmq/                       # RabbitMQ Broker (AMQP 5672 + Management UI 15672)
│
├── backend/                        # Django REST API (Port 8000)
├── chat/                           # FastAPI Chat Service + Chat DB (Port 8000)
├── mail/                           # FastAPI Mail Service (Port 8000)
├── payment/                        # Spring Boot Payment Service + Payment DB (Port 8080)
├── notification/                   # Spring Boot Notification Service + Notification DB (Port 8081)
│
├── frontend/                       # React Web Client (Port 3000)
├── raki-page/                      # Next.js Landing Page (Port 3000)
│
└── ingress/                        # NGINX Ingress Routing (WebSockets, API Rewrites)
```

---

## 2. Hướng Dẫn Triển Khai Nhanh

### Bước 1: Kiểm tra trước cấu hình (Dry Run)
```bash
kubectl apply --dry-run=client -k k8s/
```

### Bước 2: Triển khai toàn bộ hệ thống
```bash
kubectl apply -k k8s/
```

### Bước 3: Chạy Database Migration Jobs
```bash
# Thực hiện migrate schema cho Django Backend và Chat Service
kubectl apply -f k8s/migration-job.yaml

# Kiểm tra log quá trình migrate
kubectl logs -f job/backend-migration-job -n raki
kubectl logs -f job/chat-db-migration-job -n raki
```

### Bước 4: Kiểm tra trạng thái Pods và Services
```bash
# Xem toàn bộ tài nguyên trong namespace raki
kubectl get all -n raki

# Kiểm tra log của một service cụ thể (ví dụ backend)
kubectl logs -f deployment/backend -n raki

# Xem trạng thái ingress
kubectl get ingress -n raki
```

---

## 3. Cổng Truy Cập & Ingress Routing

Ingress Controller được cấu hình để định tuyến các đường dẫn như sau:

| Đường dẫn | Service Đích | Giao thức / Cổng | Ghi chú |
| :--- | :--- | :--- | :--- |
| `/` | `raki-page` | HTTP (3000) | Landing page Next.js |
| `/app/` | `frontend` | HTTP (3000) | React App |
| `/api/` | `backend` | HTTP (8000) | Django REST Framework API |
| `/api/chat/` | `chat-service` | HTTP (8000) | FastAPI Chat API (Rewrite) |
| `/api/chat/ws/` | `chat-service` | WebSocket (8000) | Chat Realtime (WebSocket Upgrade) |
| `/api/payment/` | `payment-service`| HTTP (8080) | Spring Boot Payment API (Rewrite) |
| `/api/notifications/` | `notification-service` | HTTP/WS (8081) | Notification API & WebSocket |

---

## 4. Xóa Triển Khai (Dọn Dẹp)
```bash
kubectl delete -k k8s/
```
