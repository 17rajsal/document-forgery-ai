import os
import sys
import logging
from typing import Dict, Any, Optional
from PIL import Image

logger = logging.getLogger("document_forgery_ai.ml_detector")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

MODEL_PATH = os.path.join(ROOT_DIR, "models", "document_forgery_model.pth")


def predict_document_ml(image_input) -> Dict[str, Any]:
    """
    Safe wrapper for deep learning document forgery inference.
    Fails gracefully if the model checkpoint has not been trained yet.
    """
    if not os.path.exists(MODEL_PATH):
        return {
            "available": False,
            "reason": f"Model checkpoint not found at {MODEL_PATH}. Training required.",
        }

    try:
        from infer import predict_image
        result = predict_image(image_input, model_path=MODEL_PATH)
        return {
            "available": True,
            "prediction": result["prediction"],
            "confidence_score": result["confidence_score"],
            "class_probabilities": result["class_probabilities"],
            "selected_device": result["selected_device"],
            "model_architecture": result.get("model_architecture", "mobilenet_v3_small"),
        }
    except Exception as e:
        logger.warning(f"Deep learning inference encountered an error: {e}")
        return {
            "available": False,
            "reason": str(e),
        }
