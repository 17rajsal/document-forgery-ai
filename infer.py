import os
import sys
import json
import argparse
from typing import Dict, Any, Union

import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms, models

from train import build_model, IMAGE_SIZE, CLASS_TO_IDX, IDX_TO_CLASS

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))
DEFAULT_MODEL_PATH = os.path.join(MODELS_DIR, "document_forgery_model.pth")

# Global singleton cache for model
_CACHED_MODEL = None
_CACHED_DEVICE = None
_CACHED_CHECKPOINT = None


def get_eval_transform():
    return transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def load_inference_model(model_path: str = DEFAULT_MODEL_PATH, device: torch.device = None):
    global _CACHED_MODEL, _CACHED_DEVICE, _CACHED_CHECKPOINT

    if _CACHED_MODEL is not None:
        return _CACHED_MODEL, _CACHED_DEVICE, _CACHED_CHECKPOINT

    if device is None:
        if torch.cuda.is_available():
            device = torch.device("cuda:0")
        else:
            device = torch.device("cpu")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at '{model_path}'. Run training first.")

    checkpoint = torch.load(model_path, map_location=device)
    arch = checkpoint.get("arch", "mobilenet_v3_small")

    model = build_model(arch=arch, pretrained=False).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    _CACHED_MODEL = model
    _CACHED_DEVICE = device
    _CACHED_CHECKPOINT = checkpoint
    return model, device, checkpoint


def predict_image(
    image_input: Union[str, Image.Image],
    model_path: str = DEFAULT_MODEL_PATH
) -> Dict[str, Any]:
    """
    Predicts document authenticity (genuine vs. forged) with class probabilities and confidence.
    """
    # 1. Load image
    if isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise FileNotFoundError(f"Image not found at '{image_input}'")
        image = Image.open(image_input).convert("RGB")
        image_path = image_input
    elif isinstance(image_input, Image.Image):
        image = image_input.convert("RGB")
        image_path = "PIL.Image"
    else:
        raise ValueError("image_input must be a file path string or PIL.Image instance")

    # 2. Load model
    model, device, checkpoint = load_inference_model(model_path)
    transform = get_eval_transform()
    tensor = transform(image).unsqueeze(0).to(device)

    # 3. Forward pass
    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

    # Mapping: 0 -> genuine, 1 -> forged
    prob_genuine = float(probabilities[0])
    prob_forged = float(probabilities[1])

    pred_idx = int(np.argmax(probabilities))
    pred_label = "genuine" if pred_idx == 0 else "forged"
    confidence_score = float(probabilities[pred_idx]) * 100.0

    device_str = "cuda:0" if device.type == "cuda" else "cpu"

    return {
        "image_path": image_path,
        "prediction": pred_label,
        "confidence_score": round(confidence_score, 2),
        "class_probabilities": {
            "genuine": round(prob_genuine, 4),
            "forged": round(prob_forged, 4),
        },
        "selected_device": device_str,
        "model_architecture": checkpoint.get("arch", "mobilenet_v3_small"),
        "best_epoch": checkpoint.get("best_epoch", "N/A"),
    }


def main():
    parser = argparse.ArgumentParser(description="Document Forgery AI - Single Image Inference")
    parser.add_argument("--image", type=str, required=True, help="Path to document image file")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL_PATH, help="Path to model checkpoint")
    args = parser.parse_args()

    try:
        res = predict_image(args.image, model_path=args.model)
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"[ERROR] Inference failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
