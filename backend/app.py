import os
import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from backend.agent import VeriFactSentinelAgent
from backend.config import NEBIUS_MODEL, NEBIUS_BASE_URL, NEBIUS_API_KEY, TAVILY_API_KEY

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VeriFact Sentinel API",
    description="Autonomous Multi-Agent Tech Due-Diligence & Vulnerability Intelligence Engine powered by NVIDIA Nemotron-70B on Nebius Token Factory and Tavily AI Search.",
    version="1.1.0"
)

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
        "service": "VeriFact Sentinel Engine",
        "nebius": {
            "configured": bool(NEBIUS_API_KEY and NEBIUS_API_KEY.strip() and NEBIUS_API_KEY != "your_nebius_api_key_here"),
            "model": NEBIUS_MODEL,
            "base_url": NEBIUS_BASE_URL,
        },
        "tavily": {
            "configured": bool(TAVILY_API_KEY and TAVILY_API_KEY.strip()),
            "status": "active"
        }
    }

@app.get("/api/models")
def get_supported_models():
    return {
        "active_model": NEBIUS_MODEL,
        "supported_models": [
            {
                "id": "nvidia/llama-3.1-nemotron-70b-instruct",
                "name": "NVIDIA Llama-3.1 Nemotron 70B Instruct",
                "provider": "Nebius Token Factory",
                "tier": "Heavy Reasoning & Verification",
                "recommended": True
            },
            {
                "id": "nvidia/nemotron-3-super-120b-a12b",
                "name": "NVIDIA Nemotron 3 Super",
                "provider": "Nebius Token Factory",
                "tier": "Fast Daily Calls & Routing",
                "recommended": False
            },
            {
                "id": "nvidia/nemotron-4-340b-instruct",
                "name": "NVIDIA Nemotron-4 340B Instruct",
                "provider": "Nebius Token Factory",
                "tier": "Ultra High-Parameter Synthesis",
                "recommended": False
            }
        ]
    }

@app.post("/api/investigate")
def run_investigation(req: InvestigationRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Target topic or question cannot be empty.")
    
    events = []
    final_result = None
    for event in agent.run_investigation_stream(topic):
        events.append(event)
        if "result" in event:
            final_result = event["result"]
            
    return JSONResponse(content={
        "events": events,
        "result": final_result
    })

@app.get("/api/investigate/stream")
def stream_investigation(topic: str = Query(..., min_length=2)):
    if not topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required.")

    def event_generator():
        try:
            for event in agent.run_investigation_stream(topic.strip()):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Streaming exception: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# Static & UI files
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>VeriFact Sentinel: Loading Frontend...</h1>")
