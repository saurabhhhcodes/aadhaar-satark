# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy dependency definitions
COPY frontend/package*.json ./
RUN npm install

# Copy source and build
COPY frontend/ .
# Enable static export
ENV NEXT_PUBLIC_API_URL=https://aadhaar-satark.onrender.com
RUN npm run build

# Stage 2: Setup Python Backend
FROM python:3.10-slim
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy Backend Code
COPY backend/ ./backend/

# Copy Built Static Files from Stage 1
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# Environment Variables
ENV PORT=8000

# Start Command
# Navigate to backend directory and run uvicorn
CMD ["sh", "-c", "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"]
