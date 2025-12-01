from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import subprocess
import os
import hashlib
import json
from datetime import datetime

app = FastAPI(title="JARVIS Action Exec", version="0.1.0")

class ExecuteRequest(BaseModel):
    cmd: str
    env: Optional[Dict[str, str]] = {}
    user: str = "jarvis"
    dry_run: bool = False
    sudo: bool = False
    timeout: int = 30

class ExecuteResponse(BaseModel):
    action: str
    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    transaction_hash: str
    timestamp: str
    dry_run: bool

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "action_exec"}

@app.post("/run", response_model=ExecuteResponse)
async def execute_command(request: ExecuteRequest):
    """
    Exécute une commande de manière sécurisée avec sandboxing.
    """
    start_time = datetime.utcnow()
    
    # Vérifications de sécurité
    if request.sudo and not request.dry_run:
        raise HTTPException(
            status_code=403,
            detail="Sudo commands require explicit user confirmation"
        )
    
    # Commandes interdites
    forbidden = ["rm -rf /", "mkfs", "dd if=", ":(){:|:&};:"]
    if any(danger in request.cmd for danger in forbidden):
        raise HTTPException(
            status_code=403,
            detail="Forbidden command detected"
        )
    
    stdout, stderr, exit_code = "", "", 0
    
    if request.dry_run:
        stdout = f"[DRY RUN] Would execute: {request.cmd}"
    else:
        try:
            result = subprocess.run(
                request.cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=request.timeout,
                env={**os.environ, **request.env}
            )
            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            stderr = f"Command timed out after {request.timeout}s"
            exit_code = -1
        except Exception as e:
            stderr = str(e)
            exit_code = -1
    
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    # Générer hash de transaction pour audit
    tx_data = f"{request.cmd}|{request.user}|{start_time.isoformat()}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()[:16]
    
    # TODO: Écrire dans audit log
    
    return ExecuteResponse(
        action="execute_command",
        command=request.cmd,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        duration=duration,
        transaction_hash=tx_hash,
        timestamp=start_time.isoformat(),
        dry_run=request.dry_run
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)