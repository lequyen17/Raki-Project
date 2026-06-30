# Step 1: Sử dụng Python bản lightweight (slim) để giảm kích thước image
FROM python:3.11-slim

# Step 2: Đặt thư mục làm việc bên trong container là /app
WORKDIR /app

# Step 3: Copy file requirements trước để tận dụng Docker cache (tăng tốc độ build sau này)
COPY requirements.txt .

# Step 4: Cài đặt các thư viện không dùng cache của pip để giảm dung lượng image
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy toàn bộ code từ máy của bạn vào thư mục /app trong container
COPY . .

# Step 6: Mở port 8000 của container để bên ngoài có thể truy cập
EXPOSE 8000       

# Step 7: Lệnh để chạy FastAPI khi container khởi động
# Chú ý: Đổi host thành 0.0.0.0 để Docker có thể map port ra máy thật
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]  