from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np
import os
from datetime import datetime

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics not installed. Object detection disabled.")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: pytesseract not installed. OCR disabled.")

class VisionEngine:
    """Moteur de vision artificielle avec YOLO, OCR et face detection."""
    
    def __init__(self, yolo_model: str = "yolov8n.pt"):
        self.yolo_model_name = yolo_model
        self.yolo = None
        self.face_cascade = None
        
        # Charger YOLO
        if YOLO_AVAILABLE:
            try:
                print(f"📥 Loading YOLO model '{yolo_model}'...")
                self.yolo = YOLO(yolo_model)
                print(f"✅ YOLO model loaded: {yolo_model}")
            except Exception as e:
                print(f"❌ Failed to load YOLO: {e}")
        
        # Charger Haar Cascade pour détection visages
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            print("✅ Face detection cascade loaded")
        except Exception as e:
            print(f"⚠️ Face detection unavailable: {e}")
    
    def detect_objects(self, image: np.ndarray, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Détecte les objets dans une image avec YOLO."""
        
        if not self.yolo:
            return []
        
        try:
            results = self.yolo(image, conf=confidence_threshold, verbose=False)
            
            detected_objects = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Extraire infos
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    
                    detected_objects.append({
                        "class_name": class_name,
                        "confidence": round(confidence, 2),
                        "bbox": [float(x1), float(y1), float(x2 - x1), float(y2 - y1)]
                    })
            
            return detected_objects
        
        except Exception as e:
            print(f"Object detection error: {e}")
            return []
    
    def extract_text(self, image: np.ndarray, lang: str = "fra+eng") -> List[Dict[str, Any]]:
        """Extrait le texte d'une image avec OCR Tesseract."""
        
        if not TESSERACT_AVAILABLE:
            return []
        
        try:
            # Prétraitement pour améliorer OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # OCR avec données de position
            data = pytesseract.image_to_data(gray, lang=lang, output_type=pytesseract.Output.DICT)
            
            ocr_results = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text and int(data['conf'][i]) > 30:  # Confiance min 30%
                    ocr_results.append({
                        "text": text,
                        "confidence": int(data['conf'][i]) / 100.0,
                        "bbox": [
                            int(data['left'][i]),
                            int(data['top'][i]),
                            int(data['width'][i]),
                            int(data['height'][i])
                        ]
                    })
            
            return ocr_results
        
        except Exception as e:
            print(f"OCR error: {e}")
            return []
    
    def detect_faces(self, image: np.ndarray) -> Tuple[int, List[Dict[str, Any]]]:
        """Détecte les visages dans une image."""
        
        if not self.face_cascade:
            return 0, []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            face_data = []
            for (x, y, w, h) in faces:
                face_data.append({
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "confidence": 0.9  # Haar cascade ne donne pas de score
                })
            
            return len(faces), face_data
        
        except Exception as e:
            print(f"Face detection error: {e}")
            return 0, []
    
    def analyze_scene(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyse complète d'une scène (objets + dominance couleurs)."""
        
        try:
            # Calculer couleur dominante
            pixels = image.reshape(-1, 3)
            pixels = np.float32(pixels)
            
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            k = 5
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Couleur la plus présente
            dominant_colors = centers.astype(int).tolist()
            
            # Luminosité moyenne
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            return {
                "dominant_colors": dominant_colors,
                "brightness": float(brightness),
                "is_dark": brightness < 100,
                "is_bright": brightness > 180
            }
        
        except Exception as e:
            print(f"Scene analysis error: {e}")
            return {}