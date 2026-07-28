FROM maven:3.9.6-eclipse-temurin-21-alpine

WORKDIR /app

# Chỉ copy pom.xml trước để tận dụng Docker cache cho các thư viện (Dependencies)
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src

# Lệnh mặc định sẽ chạy Spring Boot dưới dạng dòng lệnh phát triển
# Lệnh này kết hợp với Spring Boot DevTools sẽ kích hoạt chế độ tự reload khi code thay đổi
CMD ["mvn", "spring-boot:run"]