from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

app = FastAPI(title="JARVIS LLM Agent", version="0.1.0")

class ThinkRequest(BaseModel):
    user_id: str
    input: str
    context: Optional[List[str]] = []
    tools: Optional[List[str]] = []

class ThinkResponse(BaseModel):
    id: str
    plan: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    explanation: str
    need_user_confirmation: bool
    safety: Dict[str, Any]

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "llm_agent", "timestamp": datetime.utcnow().isoformat()}

@app.post("/think", response_model=ThinkResponse)
async def think(request: ThinkRequest):
    """
    Endpoint principal de raisonnement et planification.
    TODO: Intégrer LLM local (Llama via llama-cpp-python)
    TODO: Charger system prompt depuis prompts/system_jarvis_fr.txt
    TODO: Récupérer contexte mémoire depuis Chroma
    TODO: Générer plan et tool_calls
    """
    # Placeholder response pour MVP
    return ThinkResponse(
        id=f"tx-{datetime.utcnow().timestamp()}",
        plan=[{"step": 1, "desc": "Analyse de la demande", "tool": None, "args": {}}],
        tool_calls=[],
        explanation="Module LLM en cours d'implémentation. Réponse placeholder.",
        need_user_confirmation=False,
        safety={"level": "low", "notes": "Aucune action exécutée"}
    )

@app.get("/")
async def root():
    return {"message": "JARVIS LLM Agent API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)