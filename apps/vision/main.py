from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from datetime import datetime
import time
from vision_engine import VisionEngine

app = FastAPI(title="JARVIS Vision Service", version="0.2.0")

# Initialiser Vision
yolo_model = os.getenv("YOLO_MODEL", "yolov8n.pt")  # n=nano, s=small, m=medium
vision_engine = VisionEngine(yolo_model=yolo_model)

class DetectedObject(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]

class OCRResult(BaseModel):
    text: str
    confidence: float
    bbox: List[int]

class FaceData(BaseModel):
    bbox: List[int]
    confidence: float

class VisionAnalysisResponse(BaseModel):
    objects: List[DetectedObject]
    ocr_results: List[OCRResult]
    faces_count: int
    faces_data: List[FaceData]
    scene_analysis: Dict[str, Any]
    image_size: Dict[str, int]
    timestamp: str
    processing_time: float

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "vision",
        "models": {
            "yolo": vision_engine.yolo is not None,
            "face_detection": vision_engine.face_cascade is not None,
            "ocr": True  # Tesseract via pytesseract
        },
        "yolo_model": yolo_model
    }

@app.post("/analyze", response_model=VisionAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    detect_objects: bool = Form(True),
    detect_text: bool = Form(True),
    detect_faces: bool = Form(False),
    analyze_scene: bool = Form(False),
    ocr_language: str = Form("fra+eng")
):
    """
    Analyse complète d'une image.
    - Détection d'objets (YOLO)
    - OCR (Tesseract)
    - Détection de visages
    - Analyse de scène
    """
    start_time = time.time()
    
    try:
        # Lire l'image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        height, width = img.shape[:2]
        
        # Détection objets
        objects = []
        if detect_objects:
            objects_raw = vision_engine.detect_objects(img)
            objects = [DetectedObject(**obj) for obj in objects_raw]
        
        # OCR
        ocr_results = []
        if detect_text:
            ocr_raw = vision_engine.extract_text(img, lang=ocr_language)
            ocr_results = [OCRResult(**ocr) for ocr in ocr_raw]
        
        # Détection visages
        faces_count = 0
        faces_data = []
        if detect_faces:
            faces_count, faces_raw = vision_engine.detect_faces(img)
            faces_data = [FaceData(**face) for face in faces_raw]
        
        # Analyse scène
        scene_analysis = {}
        if analyze_scene:
            scene_analysis = vision_engine.analyze_scene(img)
        
        processing_time = time.time() - start_time
        
        return VisionAnalysisResponse(
            objects=objects,
            ocr_results=ocr_results,
            faces_count=faces_count,
            faces_data=faces_data,
            scene_analysis=scene_analysis,
            image_size={"width": width, "height": height},
            timestamp=datetime.utcnow().isoformat(),
            processing_time=round(processing_time, 2)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/objects")
async def detect_objects_only(file: UploadFile = File(...), confidence: float = Form(0.5)):
    """Endpoint spécialisé pour détection d'objets uniquement."""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        objects = vision_engine.detect_objects(img, confidence_threshold=confidence)
        return {"objects": objects, "count": len(objects)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/text")
async def detect_text_only(file: UploadFile = File(...), language: str = Form("fra+eng")):
    """Endpoint spécialisé pour OCR uniquement."""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        text_results = vision_engine.extract_text(img, lang=language)
        full_text = " ".join([r["text"] for r in text_results])
        
        return {
            "text": full_text,
            "detailed_results": text_results,
            "words_count": len(text_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """Liste des modèles Vision disponibles."""
    return {
        "object_detection": [
            {"name": "YOLOv8n", "speed": "fastest", "accuracy": "good"},
            {"name": "YOLOv8s", "speed": "fast", "accuracy": "better"},
            {"name": "YOLOv8m", "speed": "medium", "accuracy": "high"},
            {"name": "YOLOv8l", "speed": "slow", "accuracy": "very high"}
        ],
        "ocr": [
            {"engine": "Tesseract", "languages": ["fra", "eng", "deu", "spa", "ita"]}
        ],
        "face_detection": [
            {"method": "Haar Cascade", "speed": "fast", "accuracy": "medium"}
        ],
        "current": {
            "yolo": yolo_model,
            "ocr": "tesseract",
            "faces": "haar_cascade"
        }
    }

import os

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)