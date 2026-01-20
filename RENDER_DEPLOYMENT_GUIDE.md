# Aadhaar Satark: Render Deployment Guide

## 1. Prerequisites
- A GitHub repository containing this code.
- A [Render.com](https://render.com) account.

## 2. Environment Variables
You will need to set these in the Render Dashboard for the **Backend Service**.

| Variable Name | Value / Description |
| :--- | :--- |
| `DATA_GOV_API_KEY` | Your Data.Gov.in API Key (Required for Sync) |
| `PYTHON_VERSION` | `3.10.0` (Recommended) |

## 3. Deployment Strategy
We will deploy two services:
1.  **Backend API** (Python/FastAPI)
2.  **Frontend App** (Next.js Node Server)

### Step 1: Deploy Backend (Web Service)
1.  Click **New +** -> **Web Service**.
2.  Connect your GitHub Repo.
3.  **Name**: `aadhaar-satark-backend`
4.  **Root Directory**: `backend`
5.  **Runtime**: `Python 3`
6.  **Build Command**: `pip install -r requirements.txt`
7.  **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
8.  **Environment Variables**: Add `DATA_GOV_API_KEY`.
9.  **Deploy**. Copy the URL (e.g., `https://aadhaar-satark-backend.onrender.com`).

### Step 2: Deploy Frontend (Web Service)
1.  Click **New +** -> **Web Service**.
2.  Connect your GitHub Repo.
3.  **Name**: `aadhaar-satark-frontend`
4.  **Root Directory**: `frontend`
5.  **Runtime**: `Node`
6.  **Build Command**: `npm install && npm run build`
7.  **Start Command**: `npm start`
8.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: **PASTE_BACKEND_URL_HERE** (e.g., `https://aadhaar-satark-backend.onrender.com`).
9.  **Deploy**.

## 4. Final Verification
Open the Frontend URL. The AI Agent and Charts should load data from the Backend URL.
