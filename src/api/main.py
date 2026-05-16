from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import os
import time
from dotenv import load_dotenv

from src.api.schemas import ChatRequest, ChatResponse, SourceChunk
from src.retrieval.retriever import Retriever
from src.llm.prompt_templates import SEBI_DISCLAIMER
from src.agent.orchestrator import FundAgent

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI
app = FastAPI(
    title="Zerodha MF Chatbot API",
    description="Backend for querying Zerodha Mutual Fund knowledge base.",
    version="0.1.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (initialized on startup)
retriever = None
agent = None

@app.on_event("startup")
async def startup_event():
    global retriever, agent
    logger.info("Initializing components...")
    
    # Initialize Retriever (Phase 1A / Fallback)
    try:
        retriever = Retriever(index_dir="data/vector_store")
        logger.info("Retriever initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize retriever: {e}")

    # Initialize Agent (Phase 3)
    try:
        agent = FundAgent()
        logger.info("Agent initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")

@app.get("/")
async def root():
    return {"message": "Groww HDFC MF Chatbot API is running."}

@app.get("/health")
async def health():
    status = {
        "status": "ok",
        "agent_loaded": agent is not None and agent.agent_executor is not None,
        "api_key_set": "GOOGLE_API_KEY" in os.environ
    }
    if not status["agent_loaded"]:
        status["status"] = "degraded"
    return status

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, chat_req: ChatRequest):
    """
    Main chat endpoint:
    Uses the Phase 3 Agent Orchestrator to handle queries dynamically,
    utilizing tools like live NAV fetching, SIP calculation, and DB search.
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent components not fully initialized.")

    start_time = time.time()
    query = chat_req.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        logger.info(f"Processing query via Agent: '{query}'")
        
        # 1. Agent Generation
        answer = agent.chat(query, user_id=chat_req.user_id)
        
        processing_time = round(time.time() - start_time, 2)
        logger.info(f"Query processed in {processing_time}s")
        
        # 2. Extract disclaimer if it was injected (cleaning up any manual ones)
        if SEBI_DISCLAIMER in answer:
            answer = answer.replace(SEBI_DISCLAIMER, "").strip()
        
        # Always provide the standardized disclaimer for compliance
        clean_disclaimer = SEBI_DISCLAIMER.replace("\n\n---\n", "").strip()
        if clean_disclaimer.startswith("*"): clean_disclaimer = clean_disclaimer[1:]
        if clean_disclaimer.endswith("*"): clean_disclaimer = clean_disclaimer[:-1]
        
        return ChatResponse(
            answer=answer,
            sources=[],
            disclaimer=clean_disclaimer.strip()
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

# To run locally: python src/api/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
