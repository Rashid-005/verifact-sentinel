import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from backend.agent import VeriFactSentinelAgent
from backend.config import NEBIUS_MODEL, NEBIUS_BASE_URL, NEBIUS_API_KEY, TAVILY_API_KEY

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VeriFact Sentinel API",
    description="Autonomous Multi-Agent Due-Diligence & Tech Risk Intelligence Engine powered by NVIDIA Nemotron-70B on Nebius Token Factory and Tavily AI Search.",
    version="1.0.0"
)

# Enable CORS for local development and hosted instances
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = VeriFactSentinelAgent()

class InvestigationRequest(BaseModel):
    topic: str

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "nebius_configured": bool(NEBIUS_API_KEY and NEBIUS_API_KEY != "your_nebius_api_key_here"),
        "nebius_model": NEBIUS_MODEL,
        "nebius_base_url": NEBIUS_BASE_URL,
        "tavily_configured": bool(TAVILY_API_KEY),
    }

@app.post("/api/investigate")
def run_investigation(req: InvestigationRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Target topic or question cannot be empty.")
    
    events = []
    final_result = None
    for event in agent.run_investigation_stream(req.topic.strip()):
        events.append(event)
        if "result" in event:
            final_result = event["result"]
            
    return {
        "events": events,
        "result": final_result
    }

@app.get("/api/investigate/stream")
def stream_investigation(topic: str):
    if not topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required.")

    def event_generator():
        try:
            for event in agent.run_investigation_stream(topic.strip()):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Mount frontend
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>VeriFact Sentinel backend is running. Frontend build in progress...</h1>")
