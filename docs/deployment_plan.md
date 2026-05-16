# Deployment Plan: Railway & Vercel

This document outlines the steps to host the **Zerodha MF Chatbot** in a production-ready environment.

## 🚀 Overview
- **Railway (Backend):** Hosts the FastAPI server and the FAISS vector store.
- **Vercel (Frontend):** Hosts the Streamlit frontend (or a Next.js frontend if you migrate in the future).
- **GitHub Actions:** Continues to handle the daily data ingestion and index updates.

---

## 1. Railway: Backend Deployment (FastAPI)

Railway is excellent for persistent Python processes.

### Steps:
1. **Connect GitHub Repo:** Create a new project on Railway and connect your GitHub repository.
2. **Environment Variables:** In the Railway dashboard, add the following variables:
   - `GOOGLE_API_KEY`: Your Google AI Studio key.
   - `GROQ_API_KEY`: Your Groq API key (if still using legacy Groq tools).
   - `PYTHONPATH`: `.`
   - `PORT`: `8000` (Railway will assign this automatically).
3. **Deployment Mode:** Railway will detect the `Dockerfile` or `Procfile`.
   - If using the `Procfile`, it will run the `web` command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`.
4. **Public URL:** Enable the "Public Domain" in Railway settings (e.g., `https://groww-mf-api.up.railway.app`).

---

## 2. Vercel: Frontend Deployment (Streamlit)

> [!NOTE]
> Streamlit is not natively supported on Vercel as a serverless function. However, you can deploy it as a "Legacy" Python app or, more ideally, host the Streamlit app as a second service on **Railway**.
>
> If you strictly want **Vercel**, you should consider migrating the frontend to **Next.js** which connects to your Railway API.

### Option A: Hosting Frontend on Railway (Recommended)
1. In the same Railway project, add a second service.
2. Set the start command to: `streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0`.
3. Add an environment variable `BACKEND_URL` pointing to your Railway Backend URL.

### Option B: Hosting on Vercel (Next.js Migration)
If you build a React/Next.js frontend:
1. Run `npx create-next-app@latest frontend-next`.
2. Deploy to Vercel via GitHub.
3. Configure `NEXT_PUBLIC_API_URL` to point to Railway.

---

## 3. Configuration Changes Required

### CORS (Cross-Origin Resource Sharing)
Since the frontend and backend will be on different domains (e.g., `.vercel.app` vs `.railway.app`), you must update the FastAPI CORS settings.

**File:** `src/api/main.py`
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.vercel.app", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend API URL
Update the frontend to dynamically use the production URL.

**File:** `frontend/app.py`
```python
import os
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
```

---

## 4. Persistent Storage & Ingestion
- **FAISS Index:** The vector store is currently local. When you deploy to Railway, the index is part of your Docker image.
- **Auto-Updates:** Ensure your GitHub Action (`ingestion-cron.yml`) is configured to commit changes back to the repo. Railway will automatically re-deploy whenever a new commit (containing the updated index) is pushed.

---

## ✅ Deployment Checklist
- [ ] `Procfile` created in root.
- [ ] `requirements.txt` includes `uvicorn` and `gunicorn`.
- [ ] Railway project connected to GitHub.
- [ ] All API keys added to Railway environment variables.
- [ ] CORS settings updated in `src/api/main.py`.
