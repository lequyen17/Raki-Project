# Sử dụng Node.js bản LTS ổn định
FROM node:20-alpine

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy các file quản lý thư viện vào trước
COPY package*.json ./

# Cài đặt các thư viện
RUN npm install

# Copy toàn bộ code còn lại vào container
COPY . .

# Mở port 3000 (Port mặc định của Create React App)
EXPOSE 3000

# Lệnh khởi chạy server development của CRA
CMD ["npm", "start"]