# Sử dụng bản Python chính thức gọn nhẹ (Slim) làm nền tảng
FROM python:3.12-slim

# Thiết lập các biến môi trường cần thiết cho Python trong Docker
# PYTHONDONTWRITEBYTECODE: Ngăn Python ghi các file .pyc ra đĩa
# PYTHONUNBUFFERED: Ép Python in output trực tiếp ra terminal để dễ theo dõi log
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Cài đặt các gói hệ thống cần thiết (để cài psycopg2 nếu cần build từ mã nguồn)
# Do bạn dùng psycopg2-binary nên có thể bỏ qua bước cài thư viện build nặng
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Nâng cấp pip và sao chép file requirements vào trước để tận dụng Docker Cache
RUN pip install --upgrade pip
COPY requirements.txt /app/

# Cài đặt các thư viện từ file requirements sạch bạn vừa tạo
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn backend vào thư mục làm việc trong container
COPY . /app/

# Mở cổng 8000 (cổng chạy mặc định của Django)
EXPOSE 8000

# Lệnh khởi chạy server khi container bắt đầu chạy
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]