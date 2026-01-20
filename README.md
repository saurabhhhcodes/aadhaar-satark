# Aadhaar Satark: Strategic Dashboard & Analytics 🇮🇳

![Aadhaar Satark Banner](assets/screenshots/dashboard.png)

> **Award-Winning Solution for Team: HackElite_Coders**  
> *Empowering UIDAI with Geospatial Intelligence & Satark AI Agents*

## 🚀 Impact & Vision
**Aadhaar Satark** addresses the critical challenge of **Enrolment Gaps** in Uttar Pradesh. By leveraging **Isolation Forest Anomaly Detection**, **Geospatial Mapping**, and a **RAG-Powered AI Agent**, we provide actionable intelligence to district nodal officers.

**Key Achievement**: We reduced analysis time from **3 days to 3 seconds** using our automated pipeline.

## ✨ Key Features

### 1. 🗺️ Geospatial Intelligence Hub
Visualize live enrolment deficits across 75+ districts. Interactive maps highlight critical zones requiring immediate Mobile Unit intervention.
*(See Dashboard Screenshot above)*

### 2. 🤖 Satark AI Agent (RAG)
Stop searching through PDFs. Just ask: *"Why is Lucknow lagging?"* or *"What is the penalty for biometric delays?"*.
Our agent was trained on **3 Official UIDAI Circulars** and **Live Dataset Metrics**.

![AI Agent Interaction](assets/screenshots/chat.png)

### 3. 📊 Predictive Resource Planning
Our system doesn't just show problems; it suggests solutions.
- **"Deploy 12 Kits"** to Varanasi to clear backlog.
- **"Flagged Anomaly"** in Gorakhpur (Unknown Age Groups > 15%).

## 🛠️ Tech Stack
- **Frontend**: Next.js 14, TailwindCSS, Recharts, React-Simple-Maps
- **Backend**: Python 3.10, FastAPI, Pandas, Scikit-Learn (Isolation Forest)
- **AI/LLM**: Google Gemini (via LangChain), RAG (FAISS/ChromaDB)
- **Deployment**: Render (Single Service Monorepo)

## 🚀 Deployment Guide
This project is live!

### Option 1: Live Demo
[Link to your Render App]

### Option 2: Local Setup
```bash
# 1. Clone Repo
git clone https://github.com/saurabhhhcodes/aadhaar-satark.git

# 2. Run Backend (Port 8001)
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001

# 3. Run Frontend (Port 3000)
cd frontend
npm install
npm run dev
```

## 📄 Submission Details
- **Team**: HackElite_Coders
- **Theme**: Data Analytics & AI
- **License**: MIT
