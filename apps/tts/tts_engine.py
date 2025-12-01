from typing import Optional, Dict, Any, List
import os
import tempfile
import numpy as np
from datetime import datetime

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: TTS (Coqui) not installed. TTS features limited.")

class TTSEngine:
    """Moteur de synthèse vocale Coqui TTS."""
    
    def __init__(self, model_name: str = None, gpu: bool = False):
        self.model_name = model_name or os.getenv("TTS_MODEL", "tts_models/fr/css10/vits")
        self.gpu = gpu
        self.tts = None
        self.available_models = []
        
        if TTS_AVAILABLE:
            try:
                print(f"📥 Loading TTS model '{self.model_name}'...")
                self.tts = TTS(model_name=self.model_name, gpu=gpu)
                print(f"✅ TTS model loaded: {self.model_name}")
                
                # Lister modèles disponibles
                self.available_models = TTS.list_models()
            except Exception as e:
                print(f"❌ Failed to load TTS: {e}")
    
    def synthesize(
        self,
        text: str,
        language: str = "fr",
        speaker: Optional[str] = None,
        speed: float = 1.0
    ) -> Optional[bytes]:
        """
        Synthétise du texte en audio WAV.
        Retourne les bytes audio ou None en cas d'erreur.
        """
        
        if not self.tts:
            print("TTS model not loaded")
            return None
        
        try:
            # Générer dans un fichier temporaire
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_path = tmp.name
            
            # Synthétiser
            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker=speaker,
                language=language,
                speed=speed
            )
            
            # Lire le fichier généré
            with open(output_path, 'rb') as f:
                audio_data = f.read()
            
            # Nettoyer
            os.unlink(output_path)
            
            return audio_data
        
        except Exception as e:
            print(f"Synthesis error: {e}")
            return None
    
    def synthesize_with_voice_cloning(
        self,
        text: str,
        reference_audio_path: str,
        language: str = "fr"
    ) -> Optional[bytes]:
        """
        Synthétise avec clonage de voix depuis un fichier audio de référence.
        Utile pour créer une voix JARVIS personnalisée.
        """
        
        if not self.tts:
            return None
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_path = tmp.name
            
            # Utiliser XTTS pour voice cloning si disponible
            if "xtts" in self.model_name.lower():
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=reference_audio_path,
                    language=language
                )
            else:
                # Fallback sur synthèse normale
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language=language
                )
            
            with open(output_path, 'rb') as f:
                audio_data = f.read()
            
            os.unlink(output_path)
            return audio_data
        
        except Exception as e:
            print(f"Voice cloning error: {e}")
            return None
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Retourne la liste des voix disponibles."""
        
        # Voix par défaut JARVIS
        voices = [
            {
                "id": "jarvis_fr",
                "name": "JARVIS (Français)",
                "language": "fr",
                "type": "default"
            },
            {
                "id": "jarvis_en",
                "name": "JARVIS (English)",
                "language": "en",
                "type": "default"
            }
        ]
        
        # Ajouter voix personnalisées si disponibles
        custom_voices_dir = os.getenv("CUSTOM_VOICES_DIR", "./custom_voices")
        if os.path.exists(custom_voices_dir):
            for voice_file in os.listdir(custom_voices_dir):
                if voice_file.endswith(".wav"):
                    voice_id = os.path.splitext(voice_file)[0]
                    voices.append({
                        "id": voice_id,
                        "name": voice_id.replace("_", " ").title(),
                        "language": "auto",
                        "type": "custom",
                        "path": os.path.join(custom_voices_dir, voice_file)
                    })
        
        return voices