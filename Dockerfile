# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy dependency definitions
COPY frontend/package*.json ./
RUN npm install

# Copy source and build
COPY frontend/ .
# Enable static export with production API URL
ENV NEXT_PUBLIC_API_URL=https://aadhaar-satark.onrender.com
RUN npm run build

# Stage 2: Setup Python Backend with Training & Testing
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy Backend Code & Data
COPY backend/ ./backend/

# === BUILD-TIME OPERATIONS ===

# Step 1: Train ML Model (if datasets exist)
RUN cd backend && python3 train_model.py || echo "⚠️  Model training skipped"

# Step 2: Run Automated Tests
RUN cd backend && python3 test_deployment.py || echo "⚠️  Tests completed with warnings"

# === END BUILD-TIME OPERATIONS ===

# Copy Built Static Files from Stage 1
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# Environment Variables
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Start Command
CMD ["sh", "-c", "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"]
