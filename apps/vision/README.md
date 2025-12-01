# Vision Service - Computer Vision AI

Service d'analyse visuelle utilisant YOLO pour détection d'objets et Tesseract pour OCR.

## Capacités
- Détection d'objets (YOLOv8)
- OCR multilingue (Tesseract)
- Détection de visages
- Analyse de scènes

## Installation
```bash
apt-get install tesseract-ocr tesseract-ocr-fra
pip install -r requirements.txt
```

## Endpoint principal
POST /analyze - Analyse complète d'image
```json
{
  "detect_objects": true,
  "detect_text": true,
  "detect_faces": false
}
```