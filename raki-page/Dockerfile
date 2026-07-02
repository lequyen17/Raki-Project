# Sử dụng Node.js bản Alpine nhẹ và ổn định
FROM node:20-alpine

# Thư mục làm việc trong container
WORKDIR /app

# Copy package.json và package-lock.json trước để tận dụng cache của Docker
COPY package*.json ./

# Cài đặt toàn bộ dependencies (bao gồm cả devDependencies để phục vụ việc build)
RUN npm install

# Copy toàn bộ mã nguồn của dự án vào container
COPY . .

# Build dự án Next.js sang sản phẩm production (tạo ra thư mục .next)
RUN npm run build

# Mở cổng mặc định của Next.js
EXPOSE 3000

# Chạy Next.js ở chế độ Production thay vì development
CMD ["npm", "run", "start"]