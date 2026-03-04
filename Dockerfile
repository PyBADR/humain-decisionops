# HUMAIN DecisionOps - Railway Unified Dockerfile
# This builds both frontend and backend in a single container

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
ENV NEXT_PUBLIC_API_URL=/api
RUN npm run build

# Stage 2: Build Backend
FROM python:3.11-slim AS backend-builder
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./

# Stage 3: Production Runtime
FROM python:3.11-slim AS production

# Install Node.js for Next.js standalone server
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /app/backend ./backend

# Copy frontend build
COPY --from=frontend-builder /app/frontend/.next/standalone ./frontend
COPY --from=frontend-builder /app/frontend/.next/static ./frontend/.next/static
COPY --from=frontend-builder /app/frontend/public ./frontend/public

# Copy startup script
COPY start.sh ./
RUN chmod +x start.sh

# Environment defaults
ENV PORT=8000
ENV HEURISTIC_MODE=true
ENV PYTHONUNBUFFERED=1

EXPOSE 8000 3000

CMD ["./start.sh"]
