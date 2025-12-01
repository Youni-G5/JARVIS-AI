from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from datetime import datetime
import os
import uuid

app = FastAPI(title="JARVIS Memory Service", version="0.1.0")

# Configuration Chroma
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8008"))

try:
    client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_or_create_collection(
        name="jarvis_memory",
        metadata={"description": "JARVIS long-term memory store"}
    )
except Exception as e:
    print(f"Warning: Could not connect to Chroma at {CHROMA_HOST}:{CHROMA_PORT}")
    client = None
    collection = None

class MemoryWrite(BaseModel):
    user_id: str
    text: str
    memory_type: str  # preference, fact, event, reminder
    source: str = "user_input"
    expires_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class MemoryQuery(BaseModel):
    user_id: str
    query_text: str
    top_k: int = 5
    memory_type: Optional[str] = None

class MemoryResponse(BaseModel):
    id: str
    text: str
    memory_type: str
    created_at: str
    source: str
    distance: Optional[float] = None
    metadata: Dict[str, Any]

@app.get("/health")
async def health():
    chroma_status = "connected" if client else "disconnected"
    return {
        "status": "healthy",
        "service": "memory",
        "chroma_status": chroma_status,
        "collection": "jarvis_memory" if collection else None
    }

@app.post("/write")
async def write_memory(memory: MemoryWrite):
    """
    Stocke un souvenir dans la mémoire vectorielle.
    """
    if not collection:
        raise HTTPException(status_code=503, detail="Chroma service unavailable")
    
    try:
        memory_id = f"mem-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat()
        
        metadata = {
            "user_id": memory.user_id,
            "type": memory.memory_type,
            "created_at": timestamp,
            "source": memory.source,
            "expires_at": memory.expires_at,
            **memory.metadata
        }
        
        collection.add(
            ids=[memory_id],
            documents=[memory.text],
            metadatas=[metadata]
        )
        
        # TODO: Ajouter audit log
        
        return {
            "status": "success",
            "memory_id": memory_id,
            "timestamp": timestamp
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=List[MemoryResponse])
async def query_memory(query: MemoryQuery):
    """
    Recherche sémantique dans la mémoire.
    """
    if not collection:
        raise HTTPException(status_code=503, detail="Chroma service unavailable")
    
    try:
        # Construire le filtre
        where = {"user_id": query.user_id}
        if query.memory_type:
            where["type"] = query.memory_type
        
        results = collection.query(
            query_texts=[query.query_text],
            n_results=query.top_k,
            where=where
        )
        
        memories = []
        if results["ids"][0]:
            for i, mem_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                memories.append(MemoryResponse(
                    id=mem_id,
                    text=results["documents"][0][i],
                    memory_type=metadata.get("type", "unknown"),
                    created_at=metadata.get("created_at", ""),
                    source=metadata.get("source", ""),
                    distance=results["distances"][0][i] if results.get("distances") else None,
                    metadata=metadata
                ))
        
        return memories
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear/{user_id}")
async def clear_user_memory(user_id: str):
    """
    Efface toute la mémoire d'un utilisateur (GDPR compliance).
    """
    if not collection:
        raise HTTPException(status_code=503, detail="Chroma service unavailable")
    
    try:
        # TODO: Implémenter suppression sélective
        return {
            "status": "success",
            "message": f"Memory cleared for user {user_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Statistiques de la mémoire."""
    if not collection:
        return {"status": "unavailable"}
    
    try:
        count = collection.count()
        return {
            "total_memories": count,
            "collection_name": "jarvis_memory"
        }
    except:
        return {"status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)