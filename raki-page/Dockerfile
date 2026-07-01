# Sử dụng Node.js bản Alpine
FROM node:20-alpine

# Thư mục làm việc
WORKDIR /app

# Copy package.json và package-lock.json
COPY package*.json ./

# Cài dependencies
RUN npm install

# Mở cổng mặc định của Next.js
EXPOSE 3000

# Chạy Next.js ở chế độ development
CMD ["npm", "run", "dev"]