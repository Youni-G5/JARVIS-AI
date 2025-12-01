from typing import Optional, Dict, Any
import os
import tempfile
import time
from datetime import datetime

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: faster-whisper not installed. STT features limited.")

class WhisperEngine:
    """Moteur de transcription Whisper optimisé."""
    
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        
        if WHISPER_AVAILABLE:
            try:
                print(f"📥 Loading Whisper model '{model_size}'...")
                self.model = WhisperModel(
                    model_size,
                    device=device,
                    compute_type=compute_type,
                    download_root=os.getenv("WHISPER_MODELS_DIR", "./models")
                )
                print(f"✅ Whisper model loaded: {model_size}")
            except Exception as e:
                print(f"❌ Failed to load Whisper: {e}")
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcrit un fichier audio."""
        
        if not self.model:
            return {
                "text": "[STT not available - Whisper model not loaded]",
                "confidence": 0.0,
                "language": "unknown",
                "duration": 0.0,
                "segments": []
            }
        
        try:
            start_time = time.time()
            
            # Transcription avec faster-whisper
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection
                word_timestamps=True
            )
            
            # Collecter segments
            transcription_segments = []
            full_text = []
            total_confidence = 0.0
            segment_count = 0
            
            for segment in segments:
                transcription_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "confidence": segment.avg_logprob
                })
                full_text.append(segment.text.strip())
                total_confidence += segment.avg_logprob
                segment_count += 1
            
            # Calculer confiance moyenne
            avg_confidence = (total_confidence / segment_count) if segment_count > 0 else 0.0
            # Convertir log prob en score 0-1
            confidence_score = max(0.0, min(1.0, (avg_confidence + 5) / 5))
            
            processing_time = time.time() - start_time
            
            return {
                "text": " ".join(full_text),
                "confidence": round(confidence_score, 2),
                "language": info.language,
                "duration": info.duration,
                "segments": transcription_segments,
                "processing_time": round(processing_time, 2)
            }
        
        except Exception as e:
            print(f"Transcription error: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": "error",
                "duration": 0.0,
                "segments": [],
                "error": str(e)
            }
    
    def transcribe_realtime(self, audio_chunk: bytes) -> Dict[str, Any]:
        """Transcription temps réel (streaming)."""
        # TODO: Implémenter buffer et streaming
        # Pour l'instant, fallback sur transcription classique
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_chunk)
            tmp_path = tmp.name
        
        result = self.transcribe(tmp_path)
        os.unlink(tmp_path)
        
        return result