# ==============================================================================
# ECDAT — Enterprise Cryptographic Discovery & Analysis Tool (SIH 2026, PS 26164)
# Multi-stage production container for fullstack deployment
# ==============================================================================

# Stage 1: Build React + Vite Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI Backend Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app

# Install git and essential system tools for cryptographic repository scanning
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssl \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code and resources
COPY app ./app
COPY backend ./backend
COPY schemas ./schemas
COPY test_corpus ./test_corpus
COPY tests ./tests
COPY run.py .
RUN mkdir -p config output scratch tests/external_targets

# Copy pre-built frontend distribution into place for FastAPI static serving
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose default port
EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start FastAPI application
CMD ["sh", "-c", "uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT}"]
