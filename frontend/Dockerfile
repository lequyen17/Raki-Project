# Sử dụng Node.js Alpine để giảm kích thước image
FROM node:20-alpine

# Thư mục làm việc
WORKDIR /app

# Copy package.json và package-lock.json
COPY package*.json ./

# Cài dependencies
RUN npm install

# Mở cổng của dev server
EXPOSE 3000

# Chạy môi trường development
CMD ["npm", "start"]