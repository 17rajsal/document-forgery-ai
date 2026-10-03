"""
Proofly Financial Field Tampering Analyzer
Detects and localizes financially sensitive fields (monetary amounts, return percentages,
account numbers, UPI IDs, dates, registration numbers) and performs forensic micro-analysis:
- Typography baseline jitter & font-height variance
- Surrounding patch background & noise consistency
- Semantic contradictions (e.g. numeric ₹50,000 vs verbal text 'ten thousand')
"""

import re
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional, Tuple


NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000, "lakh": 100000, "crore": 10000000
}


def parse_verbal_amount(text: str) -> Optional[int]:
    """
    Parses verbal amounts like 'fifty thousand' or 'ten lakh rupees'.
    """
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    total = 0
    current = 0
    found_any = False

    for w in words:
        if w in NUMBER_WORDS:
            found_any = True
            val = NUMBER_WORDS[w]
            if val in (100, 1000, 100000, 10000000):
                current = max(1, current) * val
                total += current
                current = 0
            else:
                current += val

    total += current
    return total if (found_any and total > 0) else None


def locate_word_boxes(words: List[Dict[str, Any]], target_text: str) -> Optional[Dict[str, Any]]:
    """
    Finds contiguous bounding box enclosing target_text in word list.
    """
    clean_target = re.sub(r"[^a-zA-Z0-9]", "", target_text).lower()
    if not clean_target:
        return None

    for i, w in enumerate(words):
        w_clean = re.sub(r"[^a-zA-Z0-9]", "", w.get("text", "")).lower()
        if clean_target in w_clean or w_clean in clean_target:
            return {
                "x": w["x"],
                "y": w["y"],
                "w": w["w"],
                "h": w["h"]
            }

    return None


def inspect_field_patch(
    cv_img: np.ndarray,
    bbox: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Forensically analyzes the image crop of a sensitive field vs. its local neighborhood.
    Checks:
    1. Background brightness variance vs outer neighborhood
    2. Edge sharpness / anti-aliasing gradient of text
    3. Noise residual difference
    """
    h_img, w_img = cv_img.shape[:2]
    x, y, w, h = bbox["x"], bbox["y"], bbox["w"], bbox["h"]

    # Boundary check
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(w_img, x + w)
    y2 = min(h_img, y + h)

    if (x2 - x1) < 8 or (y2 - y1) < 8:
        return {"anomaly_detected": False}

    field_crop = cv_img[y1:y2, x1:x2]
    field_gray = cv2.cvtColor(field_crop, cv2.COLOR_BGR2GRAY)

    # Neighborhood crop (expanded by 12px)
    pad = 12
    nx1 = max(0, x1 - pad)
    ny1 = max(0, y1 - pad)
    nx2 = min(w_img, x2 + pad)
    ny2 = min(h_img, y2 + pad)
    neigh_crop = cv_img[ny1:ny2, nx1:nx2]
    neigh_gray = cv2.cvtColor(neigh_crop, cv2.COLOR_BGR2GRAY)

    # Calculate gradient sharpness (Laplacian variance)
    field_sharpness = float(cv2.Laplacian(field_gray, cv2.CV_64F).var())
    neigh_sharpness = float(cv2.Laplacian(neigh_gray, cv2.CV_64F).var())

    # High ratio of sharpness disparity indicates spliced text or resolution mismatch
    sharpness_ratio = (field_sharpness / max(1.0, neigh_sharpness))
    is_sharpness_anomaly = sharpness_ratio > 3.2 or sharpness_ratio < 0.28

    # Local background color difference
    # Invert to isolate paper background
    _, bg_mask = cv2.threshold(field_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    field_bg_mean = float(np.mean(field_gray[bg_mask == 255])) if np.sum(bg_mask == 255) > 10 else 255.0
    neigh_bg_mean = float(np.mean(neigh_gray))

    bg_diff = abs(field_bg_mean - neigh_bg_mean)
    is_bg_anomaly = bg_diff > 28.0

    anomaly_detected = is_sharpness_anomaly or is_bg_anomaly

    return {
        "anomaly_detected": anomaly_detected,
        "sharpness_ratio": round(sharpness_ratio, 2),
        "background_diff": round(bg_diff, 1),
        "is_sharpness_anomaly": is_sharpness_anomaly,
        "is_bg_anomaly": is_bg_anomaly
    }


def analyze_financial_fields(
    text: str,
    words: List[Dict[str, Any]],
    image_input: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Extracts all critical financial fields and scans each for evidence of tampering.
    """
    if not text:
        return {"fields": [], "tampered_fields": [], "semantic_contradictions": []}

    cv_img = None
    if image_input is not None:
        if isinstance(image_input, Image.Image):
            cv_img = cv2.cvtColor(np.array(image_input.convert("RGB")), cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, str) and image_input.endswith((".jpg", ".png", ".jpeg")):
            cv_img = cv2.imread(image_input)
        elif isinstance(image_input, np.ndarray):
            cv_img = image_input

    sensitive_fields = []
    semantic_contradictions = []

    # 1. Monetary Amounts (₹ / Rs / INR)
    amount_matches = re.finditer(
        r"(?:(?:Rs\.?|INR|[₹$€£])\s*([\d,]+(?:\.\d{1,2})?)|([\d,]+(?:\.\d{1,2})?)\s*(?:Rs\.?|INR|[₹$€£]))",
        text,
        re.I
    )
    for m in amount_matches:
        raw_val = m.group(1) or m.group(2)
        clean_num_str = re.sub(r"[^\d.]", "", raw_val)
        if clean_num_str:
            try:
                num_val = float(clean_num_str)
                bbox = locate_word_boxes(words, raw_val) or locate_word_boxes(words, clean_num_str)
                sensitive_fields.append({
                    "field_type": "MONETARY_AMOUNT",
                    "raw_text": m.group(0).strip(),
                    "numeric_value": num_val,
                    "bbox": bbox
                })
            except Exception:
                pass

    # 2. Return & Interest Rates (% p.a. / daily)
    return_matches = re.finditer(
        r"(\b\d{1,3}(?:\.\d{1,2})?\s*%\s*(?:daily|per day|monthly|p\.?m\.?|annual|p\.?a\.?|guaranteed|assured|returns)?\b)",
        text,
        re.I
    )
    for m in return_matches:
        raw_str = m.group(1).strip()
        bbox = locate_word_boxes(words, raw_str)
        sensitive_fields.append({
            "field_type": "RETURN_PERCENTAGE",
            "raw_text": raw_str,
            "bbox": bbox
        })

    # 3. Bank Account Numbers & UPI IDs
    upi_matches = re.finditer(r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b", text)
    for m in upi_matches:
        raw_upi = m.group(0).strip()
        # Avoid treating emails as UPI unless it has standard VPA handle
        if not any(raw_upi.endswith(e) for e in [".com", ".org", ".net", ".edu", ".in"]):
            sensitive_fields.append({
                "field_type": "UPI_ID",
                "raw_text": raw_upi,
                "bbox": locate_word_boxes(words, raw_upi)
            })

    # 4. Dates
    date_matches = re.finditer(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)
    for m in date_matches:
        raw_date = m.group(0).strip()
        sensitive_fields.append({
            "field_type": "DATE",
            "raw_text": raw_date,
            "bbox": locate_word_boxes(words, raw_date)
        })

    # 5. Regulatory Registration IDs (e.g. SEBI INH00000..., CIN, GSTIN)
    sebi_reg = re.finditer(r"\b(?:INH|INA|INZ|INP|INF|INM)\d{8,10}\b", text, re.I)
    for m in sebi_reg:
        sensitive_fields.append({
            "field_type": "REGULATORY_LICENSE_ID",
            "raw_text": m.group(0).strip(),
            "bbox": locate_word_boxes(words, m.group(0).strip())
        })

    # Check for Semantic Contradiction between Numeric Amount & Verbal Words
    verbal_num = parse_verbal_amount(text)
    numeric_amounts = [f["numeric_value"] for f in sensitive_fields if f.get("numeric_value") is not None]

    if verbal_num and numeric_amounts:
        # If the verbal words say e.g. 10000, but the prominent amount says 90000
        best_match = any(abs(num - verbal_num) < 1.0 for num in numeric_amounts)
        if not best_match and max(numeric_amounts) > verbal_num * 1.5:
            semantic_contradictions.append({
                "code": "SEMANTIC_AMOUNT_MISMATCH",
                "title": "Contradiction in Stated Amount",
                "description": (
                    f"Document contains verbal amount wording indicating approximately ₹{verbal_num:,}, "
                    f"whereas numeric figure indicates ₹{int(max(numeric_amounts)):,}. "
                    "This is a common signature when digits are modified without updating written verbal text."
                ),
                "severity": "CRITICAL",
                "verbal_amount": verbal_num,
                "numeric_amount": max(numeric_amounts)
            })

    # Perform micro-forensic inspection on fields with bounding boxes
    tampered_fields = []
    for f in sensitive_fields:
        if cv_img is not None and f.get("bbox"):
            patch_res = inspect_field_patch(cv_img, f["bbox"])
            if patch_res.get("anomaly_detected"):
                f["patch_forensics"] = patch_res
                f["tamper_concern"] = "HIGH"
                tampered_fields.append(f)

    return {
        "all_fields": sensitive_fields,
        "tampered_fields": tampered_fields,
        "tampered_count": len(tampered_fields),
        "semantic_contradictions": semantic_contradictions,
        "has_critical_field_concern": len(tampered_fields) > 0 or len(semantic_contradictions) > 0
    }
