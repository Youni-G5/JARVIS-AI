from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from datetime import datetime
from llm_engine import LLMEngine
from tools_executor import ToolsExecutor

load_dotenv()

app = FastAPI(title="JARVIS LLM Agent", version="0.2.0")

# Initialiser le moteur LLM
llm_engine = LLMEngine()
tools_executor = ToolsExecutor()

class ThinkRequest(BaseModel):
    user_id: str
    input: str
    context: Optional[List[str]] = []
    tools: Optional[List[str]] = []

class ThinkResponse(BaseModel):
    id: str
    plan: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    tool_results: Optional[List[Dict[str, Any]]] = []
    explanation: str
    need_user_confirmation: bool
    safety: Dict[str, Any]
    timestamp: str

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "llm_agent",
        "llm_loaded": llm_engine.llm is not None,
        "model_path": llm_engine.model_path,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/think", response_model=ThinkResponse)
async def think(request: ThinkRequest):
    """
    Endpoint principal de raisonnement et planification.
    1. Récupère contexte mémoire
    2. Génère plan avec LLM
    3. Exécute tool_calls si autorisé
    4. Retourne résultat structuré
    """
    try:
        # Récupérer contexte mémoire
        memory_context = await llm_engine.retrieve_memory(
            query=request.input,
            user_id=request.user_id,
            top_k=5
        )
        
        # Fusionner avec contexte fourni
        full_context = list(set(request.context + memory_context))
        
        # Générer réponse avec LLM
        llm_response = await llm_engine.generate(
            user_input=request.input,
            context=full_context,
            user_id=request.user_id
        )
        
        # Exécuter tools si pas besoin de confirmation
        tool_results = []
        if not llm_response.get('need_user_confirmation', False):
            tool_calls = llm_response.get('tool_calls', [])
            if tool_calls:
                tool_results = await tools_executor.execute_tools(tool_calls)
        
        # Générer ID transaction
        tx_id = f"tx-{datetime.utcnow().timestamp()}"
        
        return ThinkResponse(
            id=tx_id,
            plan=llm_response.get('plan', []),
            tool_calls=llm_response.get('tool_calls', []),
            tool_results=tool_results,
            explanation=llm_response.get('explanation', ''),
            need_user_confirmation=llm_response.get('need_user_confirmation', False),
            safety=llm_response.get('safety', {"level": "low", "notes": ""}),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {str(e)}")

@app.post("/confirm")
async def confirm_action(tx_id: str, approved: bool):
    """
    Confirme ou rejette une action en attente.
    TODO: Implémenter système de pending actions avec cache Redis/memory
    """
    return {
        "tx_id": tx_id,
        "approved": approved,
        "status": "Action confirmation system in development"
    }

@app.get("/")
async def root():
    return {
        "message": "JARVIS LLM Agent API",
        "version": "0.2.0",
        "docs": "/docs",
        "llm_status": "loaded" if llm_engine.llm else "not_loaded"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)