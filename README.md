https://docs.google.com/document/d/1QYBWnMjmCe0R-vZNczuPcc1BFAK_vZkt/edit

1. Cấu hình file .env
📍 File .env (ở cùng cấp với docker-compose.yml)
DB_NAME=my_database_name
DB_USER=my_user
DB_PASSWORD=my_password
DB_HOST=db
DB_PORT=5432


ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,backend,frontend


CORS_ALLOWED_ORIGINS=http://127.0.0.1:3000,http://localhost:3000


REACT_APP_API_URL=http://localhost:8000





2. Docker Compose 



services:


 db:
   image: postgres:15-alpine
   environment:
     POSTGRES_DB: ${DB_NAME}
     POSTGRES_USER: ${DB_USER}
     POSTGRES_PASSWORD: ${DB_PASSWORD}
   env_file:
    - .env


 backend:
   image: 103487/raki-backend:v3.0
   ports:
    - "8000:8000"
   depends_on:
    - db
   env_file:
    - .env
   environment:
     DB_NAME: ${DB_NAME}
     DB_USER: ${DB_USER}
     DB_PASSWORD: ${DB_PASSWORD}
     DB_HOST: ${DB_HOST}
     DB_PORT: ${DB_PORT}
   command: >
    sh -c "until python -c 'import socket; s = socket.socket(); s.connect((\"db\", 5432))' 2>/dev/null; do
             echo 'Đang chờ Database khởi động...';
             sleep 1;
           done;
           echo 'Database đã sẵn sàng! Bắt đầu migrate...';
           python manage.py migrate &&
           python manage.py runserver 0.0.0.0:8000"
 frontend:
   image: 103487/raki-frontend:v3.0
   ports:
    - "3000:3000"
   depends_on:
    - backend


   env_file:
    - .env



3. Chạy hệ thống lần đầu

🔹 Bước 1: Pull images

docker compose pull

🔹 Bước 2: Khởi động hệ thống

docker compose up -d

5. Access URLs


Service
URL
Frontend
http://localhost:3000
Backend
http://localhost:8000


