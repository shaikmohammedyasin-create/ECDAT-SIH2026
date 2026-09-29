# Sample Microservice Container Image
FROM python:3.10-slim

# Install OpenSSL 1.1.1 legacy crypto utilities
RUN apt-get update && apt-get install -y \
    openssl \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate legacy RSA key at container build time
RUN openssl genrsa -out /app/legacy_rsa.key 2048

ENV CRYPTO_PROVIDER="OpenSSL-Legacy"
ENV CIPHER_MODE="AES-128-CBC"

EXPOSE 8080
CMD ["python", "backend_crypto.py"]
