# Stage 1 – build fat JAR
FROM sbtscala/scala-sbt:eclipse-temurin-21.0.8_9_1.12.9_3.3.7 AS builder
WORKDIR /app
COPY . .
RUN sbt assembly

# Stage 2 – minimal runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/scala-3.6.4/products-service-assembly-0.1.0.jar app.jar
EXPOSE 8081
CMD ["java", "-jar", "app.jar"]
