from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
import aiohttp

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("Warning: llama-cpp-python not installed. LLM features limited.")

class LLMEngine:
    """Moteur LLM avec support Llama local."""
    
    def __init__(self, model_path: str = None, **kwargs):
        self.model_path = model_path or os.getenv("LLM_MODEL_PATH")
        self.llm = None
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2048"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Charger system prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts/system_jarvis_fr.txt")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()
        
        # Charger user template
        template_path = os.path.join(os.path.dirname(__file__), "prompts/user_template.txt")
        with open(template_path, 'r', encoding='utf-8') as f:
            self.user_template = f.read()
        
        # Initialiser le modèle si disponible
        if self.model_path and LLAMA_AVAILABLE:
            try:
                self.llm = Llama(
                    model_path=self.model_path,
                    n_ctx=4096,
                    n_threads=8,
                    n_gpu_layers=0,  # CPU only, augmenter pour GPU
                    verbose=False
                )
                print(f"✅ LLM loaded: {self.model_path}")
            except Exception as e:
                print(f"❌ Failed to load LLM: {e}")
    
    def format_prompt(self, user_input: str, context: List[str], user_id: str) -> str:
        """Formate le prompt utilisateur avec contexte."""
        memory_snippets = "\n".join([f"- {ctx}" for ctx in context[:5]])
        
        prompt = self.user_template.replace("{{user_id}}", user_id)
        prompt = prompt.replace("{{iso_timestamp}}", datetime.utcnow().isoformat())
        prompt = prompt.replace("{{retrieved_memory_snippets}}", memory_snippets or "Aucun")
        prompt = prompt.replace("{{user_text}}", user_input)
        
        return prompt
    
    async def generate(self, user_input: str, context: List[str], user_id: str) -> Dict[str, Any]:
        """Génère une réponse avec plan et tool calls."""
        
        # Formater le prompt
        user_prompt = self.format_prompt(user_input, context, user_id)
        full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
        
        # Si modèle local disponible
        if self.llm:
            try:
                output = self.llm(
                    full_prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stop=["\n\n", "USER:"],
                    echo=False
                )
                
                response_text = output['choices'][0]['text'].strip()
                
                # Parser la réponse JSON si possible
                try:
                    response_data = json.loads(response_text)
                    return response_data
                except json.JSONDecodeError:
                    # Fallback: réponse textuelle
                    return {
                        "plan": [{"step": 1, "desc": "Répondre à l'utilisateur", "tool": None, "args": {}}],
                        "tool_calls": [],
                        "explanation": response_text,
                        "need_user_confirmation": False,
                        "safety": {"level": "low", "notes": "Réponse conversationnelle"}
                    }
            
            except Exception as e:
                print(f"LLM generation error: {e}")
                return self._fallback_response(user_input)
        
        else:
            # Fallback sans modèle local
            return self._fallback_response(user_input)
    
    def _fallback_response(self, user_input: str) -> Dict[str, Any]:
        """Réponse par défaut quand LLM non disponible."""
        return {
            "plan": [
                {"step": 1, "desc": "Analyser la demande", "tool": None, "args": {}},
                {"step": 2, "desc": "Informer l'utilisateur", "tool": "notify", "args": {"message": "LLM en cours de chargement"}}
            ],
            "tool_calls": [],
            "explanation": f"J'ai bien reçu votre demande: '{user_input}'. Le module LLM est en cours de chargement. Pour l'instant, je peux exécuter des actions simples.",
            "need_user_confirmation": False,
            "safety": {"level": "low", "notes": "Mode fallback actif"}
        }
    
    async def retrieve_memory(self, query: str, user_id: str, top_k: int = 5) -> List[str]:
        """Récupère le contexte depuis le service Memory."""
        memory_host = os.getenv("MEMORY_HOST", "localhost:8003")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{memory_host}/query",
                    json={
                        "user_id": user_id,
                        "query_text": query,
                        "top_k": top_k
                    }
                ) as resp:
                    if resp.status == 200:
                        memories = await resp.json()
                        return [mem['text'] for mem in memories]
        except Exception as e:
            print(f"Memory retrieval error: {e}")
        
        return []