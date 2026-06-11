FROM node:20-alpine

WORKDIR /app

# Sao chép file quản lý thư viện vào trước
COPY package*.json ./

# Cài đặt các thư viện cần thiết
RUN npm install

# Sao chép toàn bộ code còn lại vào container
COPY . .

# Build dự án Next.js sang production
RUN npm run build

# Next.js mặc định chạy cổng 3000
EXPOSE 3000

CMD ["npm", "start"]