# Groww Mutual Fund (MF) Chatbot

This repository contains the Phase-wise implementation of the Groww MF Chatbot, an AI-powered assistant built to answer mutual fund queries using a Retrieval-Augmented Generation (RAG) pipeline.

Currently, **Phase 4** (Production Hardening) is completed.
The chatbot is now production-ready with agentic capabilities, safety guardrails, and observability.

### Key Features (Phase 4):
- **Agentic AI**: Real-time NAV fetching, SIP calculation, and fund comparison.
- **Safety Guardrails**: Prompt injection detection and off-topic filtering.
- **PII Redaction**: Automatic masking of sensitive user data (PAN, Aadhaar).
- **Observability**: Latency tracking and event logging.
- **Human Escalation**: Simulated support ticket creation for complex queries.
- **Docker Support**: Containerized for easy deployment.


## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Google Gemini API Key (`GOOGLE_API_KEY`)

### 2. Installation
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and add your Google API key:
```bash
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY=your_actual_key_here
```

### 4. Run Phase 0 Data Ingestion
Before the chatbot can answer questions, it needs to scrape and embed the data.
```bash
playwright install chromium
python scripts/run_ingestion.py
```
This will build the local FAISS vector store in `data/vector_store/`.

## Running the Chatbot

You need to run both the FastAPI backend and the Streamlit frontend.

### 1. Start the FastAPI Backend
In a terminal window, run:
```bash
uvicorn src.api.main:app --reload
```
The API will be available at `http://localhost:8000`. You can test the endpoints using Swagger UI at `http://localhost:8000/docs`.

### 2. Start the Streamlit UI
In a separate terminal window, run:
```bash
streamlit run frontend/app.py
```
This will open the user-friendly chat interface in your browser.

## Testing

To run the integration and edge-case tests for Phase 1:
```bash
pip install pytest httpx
pytest tests/test_phase1.py -v
```

## Architecture
See `docs/Architecture_Phasewise.md` for a full breakdown of the phase-wise development plan, edge cases, and architectural diagrams.
