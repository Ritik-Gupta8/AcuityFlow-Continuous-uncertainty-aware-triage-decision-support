# 🚀 AcuityFlow - Free Cloud Deployment Guide

This guide provides step-by-step instructions to deploy both the **FastAPI Backend** and **Next.js Frontend** of AcuityFlow **100% free**, with HTTPS, automatic CI/CD on git push, and zero infrastructure maintenance.

---

## 🎯 Architecture Overview for Deployment

```
   +---------------------------+         +---------------------------+
   |      Vercel / Netlify     |         |       Render / Koyeb      |
   |    Next.js 14 Frontend    | --REST->|     FastAPI ML Backend    |
   |   (Free Global CDN Edge)  |  Calls  |   (Free Web Service Tier) |
   +---------------------------+         +---------------------------+
```

---

## Option 1: Render (Backend) + Vercel (Frontend) ⭐ [Recommended - Fastest & 100% Free]

### Part A: Deploy the Backend on Render (Free Tier)
1. **Push your code to GitHub**:
   Make sure your repository has the latest code pushed to `main`.
2. **Sign Up / Log In to Render**:
   - Go to https://render.com and log in with GitHub.
3. **Create a New Web Service**:
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repository.
4. **Configure the Service**:
   - **Name**: `acuityflow-backend` (or your choice)
   - **Region**: Choose the closest region (e.g., *Singapore*, *Frankfurt*, *Oregon*)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
   - **Instance Type**: **Free** (0.1 CPU, 512 MB RAM)
5. **Add Environment Variables**:
   In the **Environment** tab, add:
   - `APP_ENV` = `production`
   - `PYTHONUNBUFFERED` = `1`
   - `PORT` = `10000`
   - `GEMINI_API_KEY` = `your_gemini_key` *(optional, system falls back to regex if omitted)*
6. **Deploy**:
   - Click **Create Web Service**.
   - Wait 2-3 minutes for build & deployment.
   - Copy your public backend URL (e.g., `https://acuityflow-backend.onrender.com`).
   - Test by opening `https://acuityflow-backend.onrender.com/health` or `/docs`.

---

### Part B: Deploy the Frontend on Vercel (Free Tier)
1. **Sign Up / Log In to Vercel**:
   - Go to https://vercel.com and log in with GitHub.
2. **Import Project**:
   - Click **Add New...** -> **Project**.
   - Select your AcuityFlow repository.
3. **Configure Project Settings**:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click *Edit* and select `frontend`.
4. **Set Environment Variables**:
   - Add Key: `NEXT_PUBLIC_API_BASE_URL`
   - Value: `https://acuityflow-backend.onrender.com` *(your Render backend URL from Part A)*
5. **Deploy**:
   - Click **Deploy**.
   - In ~60 seconds, Vercel will give you a live production URL (e.g., `https://acuityflow.vercel.app`).

---

## Option 2: Google Cloud Run (Using Free Tier / Google Cloud Credits)

Google Cloud Run offers **2 million requests/month free** and scales to 0 instances when idle.

### Backend Deployment to Cloud Run:
1. **Install Google Cloud SDK** (`gcloud`) or use Google Cloud Shell.
2. **Authenticate & Select Project**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_GCP_PROJECT_ID
   ```
3. **Deploy Backend using Cloud Build & Cloud Run**:
   ```bash
   cd backend
   gcloud run deploy acuityflow-backend \
     --source . \
     --platform managed \
     --region asia-south1 \
     --allow-unauthenticated \
     --min-instances 0 \
     --max-instances 2 \
     --memory 512Mi \
     --cpu 1
   ```
4. **Copy the Service URL**:
   Cloud Run outputs a URL like `https://acuityflow-backend-xyz.a.run.app`.

---

## 🔒 Post-Deployment Checklist & Verification

1. **Verify Backend Health & CORS**:
   - Open `https://<YOUR_BACKEND_URL>/health` in browser. Expected output: `{"status": "healthy"}`.
   - Test triage endpoint with a synthetic test case.
2. **Verify Frontend API Connection**:
   - Open your deployed Vercel link (`https://<YOUR_FRONTEND>.vercel.app`).
   - Confirm patient queues, vital indicators, surge toggle, and clinician override function seamlessly.
3. **Cold Starts Note (Render Free Tier)**:
   - On Render free tier, the backend spins down after 15 minutes of inactivity. The first request after sleep may take ~30-40 seconds to wake up.
   - **Pro Tip for Demo Day**: Open the backend URL 2 minutes before the presentation to pre-warm the container!

---

## 🛡️ Hackathon Submission Summary Table

| Service | Hosting Platform | Cost | Purpose |
|---|---|---|---|
| **Frontend UI** | Vercel | **$0 / Free** | Fast edge-rendered Next.js 14 Dashboard |
| **Backend API & ML Engine** | Render / Cloud Run | **$0 / Free** | FastAPI + scikit-learn calibrated risk inference |
| **Domain & SSL** | Auto Vercel / Render | **$0 / Free** | Automatic `.vercel.app` & `.onrender.com` with free TLS/HTTPS |
