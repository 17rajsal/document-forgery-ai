import os
import io
import re
import json
import base64
import numpy as np
import cv2
from PIL import Image, ImageChops, ImageEnhance, ExifTags

try:
    from document_classifier import get_standard_category, DOCUMENT_CATEGORIES, CATEGORY_DISPLAY_NAMES
except ImportError:
    from .document_classifier import get_standard_category, DOCUMENT_CATEGORIES, CATEGORY_DISPLAY_NAMES



# =========================================================
# SUSPICIOUS SOFTWARE DICTIONARY
# =========================================================

EDITING_SOFTWARE_PATTERNS = [
    (r"adobe\s*photoshop", "Adobe Photoshop (Professional Image Editor)", "CRITICAL"),
    (r"gimp", "GIMP (GNU Image Manipulation Program)", "CRITICAL"),
    (r"canva", "Canva (Online Design / Layout Tool)", "HIGH"),
    (r"picsart", "PicsArt (Mobile Photo Editor)", "HIGH"),
    (r"photopea", "Photopea (Web Image Editor)", "CRITICAL"),
    (r"paint\.net", "Paint.NET (Image Editor)", "HIGH"),
    (r"coreldraw", "CorelDraw (Vector/Layout Editor)", "HIGH"),
    (r"snapseed", "Snapseed (Photo Retouching)", "MODERATE"),
    (r"pixlr", "Pixlr (Photo Editor)", "HIGH"),
    (r"affinity", "Affinity Photo / Designer", "HIGH"),
    (r"photofiltre", "PhotoFiltre", "HIGH"),
    (r"acrobat", "Adobe Acrobat (Document Alteration Tool)", "MODERATE"),
    (r"pdfsam", "PDFsam (PDF Split / Merge / Edit)", "MODERATE"),
    (r"foxit", "Foxit PDF Editor", "MODERATE"),
    (r"ilovepdf", "iLovePDF (Online Document Editor)", "MODERATE"),
]

# =========================================================
# DOCUMENT-TYPE FORENSIC CONFIGURATION & THRESHOLDS
# =========================================================

DEFAULT_CONFIG = {
    "categories": {
        "id_card": {
            "weights": {
                "software": 1.1,
                "ela": 1.0,
                "noise": 0.9,
                "copy_move": 1.2,
                "layout": 0.8,
                "validation": 1.3
            },
            "thresholds": {"genuine_max": 28, "forged_min": 65},
            "noise_threshold_mult": 3.0,
            "min_corroborating_signals": 2
        },
        "certificate": {
            "weights": {
                "software": 1.1,
                "ela": 1.1,
                "noise": 1.0,
                "copy_move": 1.3,
                "layout": 0.9,
                "validation": 1.1
            },
            "thresholds": {"genuine_max": 26, "forged_min": 62},
            "noise_threshold_mult": 2.8,
            "min_corroborating_signals": 2
        },
        "marksheet": {
            "weights": {
                "software": 1.0,
                "ela": 1.0,
                "noise": 0.9,
                "copy_move": 1.2,
                "layout": 1.0,
                "validation": 1.2
            },
            "thresholds": {"genuine_max": 28, "forged_min": 64},
            "noise_threshold_mult": 2.9,
            "min_corroborating_signals": 2
        },
        "invoice_receipt": {
            "weights": {
                "software": 1.0,
                "ela": 0.9,
                "noise": 0.85,
                "copy_move": 1.1,
                "layout": 0.9,
                "validation": 1.3
            },
            "thresholds": {"genuine_max": 30, "forged_min": 65},
            "noise_threshold_mult": 3.0,
            "min_corroborating_signals": 2
        },
        "general_scanned": {
            "weights": {
                "software": 1.0,
                "ela": 0.8,
                "noise": 0.8,
                "copy_move": 1.0,
                "layout": 0.7,
                "validation": 1.0
            },
            "thresholds": {"genuine_max": 32, "forged_min": 68},
            "noise_threshold_mult": 3.2,
            "min_corroborating_signals": 2
        }
    },
    "global": {
        "base_confidence": 88.0,
        "low_confidence_threshold": 60.0,
        "genuine_max_default": 28,
        "forged_min_default": 65
    }
}

def load_model_config():
    config_path = os.path.join(os.path.dirname(__file__), "model_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG

def get_category_config(category: str):
    config = load_model_config()
    cat_cfg = config.get("categories", {}).get(category)
    if not cat_cfg:
        cat_cfg = DEFAULT_CONFIG["categories"].get(category, DEFAULT_CONFIG["categories"]["general_scanned"])
    return cat_cfg


def image_to_base64_jpeg(pil_img, quality=85):
    """
    Convert a PIL image to a base64 encoded data URI.
    """
    buffer = io.BytesIO()
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    pil_img.save(buffer, format="JPEG", quality=quality)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


# =========================================================
# 1. ERROR LEVEL ANALYSIS (ELA)
# =========================================================

def perform_ela(image, quality=90, multiplier=15):
    """
    Performs Error Level Analysis (ELA) on any RGB image.
    Works for JPEG, PNG, WEBP, TIFF, BMP, and rasterized PDF pages.
    
    Includes false-positive suppression: distinguishes uniform global
    compression (e.g. social media resaving, screenshotting) from localized splicing.
    """
    original = image.convert("RGB")
    width, height = original.size

    # Re-save to JPEG in memory
    buffer = io.BytesIO()
    original.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    recompressed = Image.open(buffer).convert("RGB")

    # Calculate absolute difference
    diff = ImageChops.difference(original, recompressed)

    # Convert to numpy array
    diff_np = np.array(diff, dtype=np.float32)
    diff_gray = np.mean(diff_np, axis=2)

    avg_diff = float(np.mean(diff_gray))
    max_diff = float(np.max(diff_gray))

    # Measure spatial distribution across grid tiles to distinguish uniform vs localized delta
    tile_size = 32
    h_tiles = max(1, height // tile_size)
    w_tiles = max(1, width // tile_size)
    tile_means = []

    for ty in range(h_tiles):
        for tx in range(w_tiles):
            tile = diff_gray[ty * tile_size:(ty + 1) * tile_size, tx * tile_size:(tx + 1) * tile_size]
            if tile.size > 0:
                tile_means.append(float(np.mean(tile)))

    tile_std = float(np.std(tile_means)) if tile_means else 0.0

    # High difference anomaly calculation
    high_diff_threshold = max(12.0, avg_diff * 2.5)
    high_diff_pixels = np.count_nonzero(diff_gray > high_diff_threshold)
    total_pixels = width * height
    anomaly_ratio = float((high_diff_pixels / max(total_pixels, 1)) * 100.0)

    # Multiply difference for human visual perception
    amplified = np.clip(diff_gray * multiplier, 0, 255).astype(np.uint8)

    # Grayscale difference image
    diff_pil = Image.fromarray(amplified)
    diff_b64 = image_to_base64_jpeg(diff_pil)

    # Thermal heatmap using COLORMAP_JET
    heatmap_cv = cv2.applyColorMap(amplified, cv2.COLORMAP_JET)
    heatmap_rgb = cv2.cvtColor(heatmap_cv, cv2.COLOR_BGR2RGB)
    heatmap_pil = Image.fromarray(heatmap_rgb)
    heatmap_b64 = image_to_base64_jpeg(heatmap_pil)

    # False-positive suppression:
    # If avg_diff is elevated but tile_std is very low (< 2.2), the image has uniform
    # global compression (e.g. WhatsApp, web screenshot, repeated camera save), NOT localized tampering.
    is_uniform_global_compression = (avg_diff > 7.0 and tile_std < 2.5 and anomaly_ratio < 12.0)

    if is_uniform_global_compression:
        status = "UNIFORM_COMPRESSION"
    elif (avg_diff > 14.0 or anomaly_ratio > 20.0) and tile_std >= 3.5:
        status = "HIGH_ANOMALY"
    elif avg_diff > 7.0 or anomaly_ratio > 8.0:
        status = "MODERATE_ANOMALY"
    else:
        status = "NORMAL"

    return {
        "available": True,
        "average_difference": round(avg_diff, 2),
        "max_difference": round(max_diff, 2),
        "anomaly_ratio_pct": round(anomaly_ratio, 2),
        "spatial_variance": round(tile_std, 2),
        "is_uniform_compression": is_uniform_global_compression,
        "status": status,
        "heatmap_image": heatmap_b64,
        "diff_image": diff_b64,
    }


# =========================================================
# 2. NOISE & TEXTURE INCONSISTENCY ANALYSIS
# =========================================================

def analyze_noise_inconsistency(image, block_size=32, is_screenshot=False, threshold_multiplier=None):
    """
    Detects local noise variance anomalies across grid blocks with spatial clustering.
    Suppresses false positives caused by scattered document text lines by requiring
    contiguous cluster formation (>= 3 connected outlier blocks) for tampering detection.
    """
    cv_img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape

    laplacian = cv2.Laplacian(gray, cv2.CV_64F)

    variances = []
    blocks = []

    h_blocks = (h - block_size) // block_size + 1
    w_blocks = (w - block_size) // block_size + 1

    if h_blocks <= 0 or w_blocks <= 0:
        return {
            "available": False,
            "noise_inconsistency_score": 0.0,
            "anomaly_detected": False,
            "noise_map_image": None,
        }

    for by in range(h_blocks):
        y = by * block_size
        for bx in range(w_blocks):
            x = bx * block_size
            patch = laplacian[y:y + block_size, x:x + block_size]
            var = float(np.var(patch))
            variances.append(var)
            blocks.append((bx, by, x, y, var))

    if not variances:
        return {
            "available": False,
            "noise_inconsistency_score": 0.0,
            "anomaly_detected": False,
            "noise_map_image": None,
        }

    variances = np.array(variances)
    median_var = float(np.median(variances))
    std_var = float(np.std(variances))

    if threshold_multiplier is None:
        threshold_multiplier = 3.2 if is_screenshot else 2.6
    threshold = median_var + threshold_multiplier * std_var

    outlier_grid = np.zeros((h_blocks, w_blocks), dtype=np.uint8)
    outlier_count = 0
    noise_visual = cv_img.copy()

    for (bx, by, x, y, var) in blocks:
        if var > threshold and var > 25.0:
            outlier_count += 1
            outlier_grid[by, bx] = 1
            cv2.rectangle(
                noise_visual,
                (x, y),
                (x + block_size, y + block_size),
                (255, 45, 45),
                2
            )

    outlier_ratio = (outlier_count / max(len(blocks), 1)) * 100.0
    min_ratio = 6.0 if is_screenshot else 3.8

    # Connected component analysis on outlier grid:
    # Tampered/spliced content creates contiguous 2D regions (>= 3 connected blocks).
    # In clean digital documents (near-zero background noise), text edges naturally create
    # high Laplacian variance. Suppress noise anomaly unless actual background texture is present.
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(outlier_grid, connectivity=8)
    max_cluster_size = 0
    for lbl in range(1, num_labels):
        area = int(stats[lbl, cv2.CC_STAT_AREA])
        if area > max_cluster_size:
            max_cluster_size = area

    if median_var < 8.0:
        # Clean digital canvas - variance from text characters is not noise splicing
        has_spatial_cluster = False
        anomaly_detected = False
    else:
        has_spatial_cluster = (max_cluster_size >= 3)
        anomaly_detected = bool(outlier_ratio > min_ratio and has_spatial_cluster)

    noise_pil = Image.fromarray(noise_visual)
    noise_map_b64 = image_to_base64_jpeg(noise_pil)

    return {
        "available": True,
        "median_noise_variance": round(median_var, 2),
        "outlier_blocks_count": outlier_count,
        "outlier_ratio_pct": round(outlier_ratio, 2),
        "max_cluster_size": max_cluster_size,
        "has_spatial_cluster": has_spatial_cluster,
        "anomaly_detected": anomaly_detected,
        "noise_map_image": noise_map_b64,
    }



# =========================================================
# 3. COPY-MOVE / DUPLICATION DETECTION
# =========================================================

def detect_copy_move(image, min_cluster_matches=18):
    """
    Detects duplicated regions (cloned text, duplicate signatures, replicated stamps)
    using ORB feature detection with Lowe's ratio test and geometric displacement clustering.
    Suppresses false positives caused by repeated alphabet characters.
    """
    cv_img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)

    orb = cv2.ORB_create(nfeatures=1200)
    keypoints, descriptors = orb.detectAndCompute(gray, None)

    if descriptors is None or len(keypoints) < 20:
        return {
            "detected": False,
            "suspicious_match_count": 0,
            "description": "Insufficient distinct keypoints to evaluate copy-move duplication."
        }

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(descriptors, descriptors, k=4)

    min_spatial_distance = 75
    displacement_bins = {}

    for match_group in matches:
        if len(match_group) < 3:
            continue
        first_neighbor = match_group[1]
        second_neighbor = match_group[2]

        # Lowe's ratio test: match must be distinctively better than third closest keypoint
        if first_neighbor.distance < 38 and first_neighbor.distance < 0.78 * second_neighbor.distance:
            kp1 = keypoints[first_neighbor.queryIdx].pt
            kp2 = keypoints[first_neighbor.trainIdx].pt
            dx = kp2[0] - kp1[0]
            dy = kp2[1] - kp1[1]
            dist = np.sqrt(dx**2 + dy**2)
            if dist > min_spatial_distance:
                if dx < 0 or (dx == 0 and dy < 0):
                    dx, dy = -dx, -dy
                bin_key = (int(round(dx / 24.0)), int(round(dy / 24.0)))
                displacement_bins[bin_key] = displacement_bins.get(bin_key, 0) + 1

    max_cluster = max(displacement_bins.values()) if displacement_bins else 0
    is_suspicious = max_cluster >= min_cluster_matches

    return {
        "detected": is_suspicious,
        "suspicious_match_count": max_cluster,
        "description": (
            f"Detected {max_cluster} geometrically aligned duplicate feature clusters."
            if is_suspicious else "No duplicated feature clusters with consistent displacement detected."
        )
    }


# =========================================================
# 4. FONT & TEXT LAYOUT INCONSISTENCY DETECTION
# =========================================================

def detect_text_layout_inconsistencies(words):
    """
    Inspects OCR word bounding boxes to identify baseline shifts,
    mismatched font heights on the same line, and patched text boxes.
    """
    if not words or len(words) < 8:
        return {
            "inconsistency_detected": False,
            "suspicious_lines_count": 0,
            "description": "Insufficient OCR word tokens for text layout analysis."
        }

    # Group words into approximate lines
    words_sorted = sorted(words, key=lambda w: (w.get("y", 0), w.get("x", 0)))
    lines = []
    current_line = []
    current_y = None

    for w in words_sorted:
        wy = w.get("y", 0)
        wh = max(1, w.get("h", 10))
        if current_y is None:
            current_y = wy
            current_line.append(w)
        elif abs(wy - current_y) <= max(14, int(wh * 0.65)):
            current_line.append(w)
        else:
            if len(current_line) >= 3:
                lines.append(current_line)
            current_line = [w]
            current_y = wy

    if len(current_line) >= 3:
        lines.append(current_line)

    suspicious_lines = 0
    suspicious_details = []

    for line in lines:
        # Ignore punctuation-only or single-character words (e.g. ':', '-', '.', '/')
        sig_words = [
            w for w in line
            if len(w.get("text", "").strip()) >= 2
            and not re.match(r"^[\:\-\.\,\/\\\|\_]+$", w.get("text", "").strip())
            and w.get("h", 0) >= 8
        ]
        if len(sig_words) >= 3:
            heights = [w["h"] for w in sig_words]
            median_h = float(np.median(heights))
            if median_h > 0:
                # An anomalous spliced word deviates sharply from the median height of the line
                anomalous_words = [
                    w for w in sig_words
                    if (w["h"] / median_h > 2.0 or w["h"] / median_h < 0.48)
                ]
                if len(anomalous_words) == 1 and len(sig_words) >= 3:
                    # Single spliced word inside an otherwise uniform line
                    suspicious_lines += 1
                    suspicious_details.append(f"Word '{anomalous_words[0].get('text')}' height mismatch ({anomalous_words[0]['h']}px vs median {median_h:.0f}px)")
                elif len(anomalous_words) >= 2 and (max(heights) / min(heights)) > 2.6:
                    suspicious_lines += 1

    has_layout_tampering = bool(suspicious_lines >= 1 and suspicious_details) or (suspicious_lines >= 2)

    return {
        "inconsistency_detected": has_layout_tampering,
        "suspicious_lines_count": suspicious_lines,
        "suspicious_details": suspicious_details[:3],
        "description": (
            f"Detected {suspicious_lines} lines with anomalous word height or baseline jitter."
            if has_layout_tampering else "Text layout and baseline alignment appear consistent."
        )
    }


# =========================================================
# 5. METADATA & SOFTWARE FORENSICS
# =========================================================

def inspect_metadata(image, file_path):
    metadata_info = {
        "has_exif": False,
        "camera_make": None,
        "camera_model": None,
        "software": None,
        "date_time_original": None,
        "date_time_digitized": None,
        "date_time_modified": None,
        "editing_software_detected": False,
        "detected_software_name": None,
        "severity": "INFO",
        "raw_tags": {},
    }

    try:
        exif = image.getexif()

        if exif and len(exif) > 0:
            metadata_info["has_exif"] = True

            for tag_id, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                clean_val = str(value).strip()
                if len(clean_val) < 200:
                    metadata_info["raw_tags"][tag_name] = clean_val

                if tag_name == "Make":
                    metadata_info["camera_make"] = clean_val
                elif tag_name == "Model":
                    metadata_info["camera_model"] = clean_val
                elif tag_name == "Software":
                    metadata_info["software"] = clean_val
                elif tag_name == "DateTimeOriginal":
                    metadata_info["date_time_original"] = clean_val
                elif tag_name == "DateTimeDigitized":
                    metadata_info["date_time_digitized"] = clean_val
                elif tag_name == "DateTime":
                    metadata_info["date_time_modified"] = clean_val

        # Byte-stream signature search
        with open(file_path, "rb") as f:
            raw_bytes = f.read(262144)
            raw_text = raw_bytes.decode("latin-1", errors="ignore").lower()

        software_field = str(metadata_info["software"] or "").lower()
        combined_text = software_field + " " + raw_text

        for pattern, tool_name, severity in EDITING_SOFTWARE_PATTERNS:
            if re.search(pattern, combined_text):
                metadata_info["editing_software_detected"] = True
                metadata_info["detected_software_name"] = tool_name
                metadata_info["severity"] = severity
                break

    except Exception as e:
        metadata_info["error"] = str(e)

    return metadata_info


# =========================================================
# 6. COMPOSITE SCORING, CONFIDENCE & 4-TIER VERDICT
# =========================================================

def calculate_composite_forgery_score(
    ela_result,
    noise_result,
    copy_move_result,
    metadata_result,
    layout_result=None,
    validation_flags=None,
    document_type="Unknown",
    image_props=None,
    ml_result=None
):
    standard_cat = get_standard_category(document_type)
    cat_cfg = get_category_config(standard_cat)
    weights = cat_cfg.get("weights", {})
    thresholds = cat_cfg.get("thresholds", {"genuine_max": 28, "forged_min": 65})

    w_soft = weights.get("software", 1.0)
    w_ela = weights.get("ela", 1.0)
    w_noise = weights.get("noise", 1.0)
    w_copy = weights.get("copy_move", 1.1)
    w_layout = weights.get("layout", 0.9)
    w_valid = weights.get("validation", 1.2)

    positive_score = 0.0
    discounts = 0.0
    indicators = []

    # 1. Metadata & Software Traces
    has_critical_software = False
    if metadata_result.get("editing_software_detected"):
        tool = metadata_result.get("detected_software_name", "Photo Editing Tool")
        severity = metadata_result.get("severity", "CRITICAL")
        if severity == "CRITICAL":
            pts = 38.0 * w_soft
            has_critical_software = True
        elif severity == "HIGH":
            pts = 26.0 * w_soft
            has_critical_software = True
        else:
            pts = 14.0 * w_soft

        positive_score += pts
        indicators.append({
            "code": "EDITING_SOFTWARE_TRACES",
            "title": f"Editing Software Signature Detected ({tool})",
            "description": f"File contains binary signatures of {tool}. Scanned documents rarely contain image manipulation tags.",
            "severity": severity,
            "weight": round(pts, 1),
        })
    elif metadata_result.get("has_exif"):
        discounts += 8.0
        indicators.append({
            "code": "VALID_EXIF",
            "title": "Hardware/Scanner EXIF Present",
            "description": f"Image contains valid hardware metadata ({metadata_result.get('camera_model', 'Camera/Scanner')}). Genuine device signature verified.",
            "severity": "VERIFIED",
            "weight": -8,
        })
    else:
        # Missing EXIF is common in scans/web/chat apps; do NOT penalize as forgery
        indicators.append({
            "code": "NO_EXIF",
            "title": "No Hardware EXIF (Normal for Web/Scans)",
            "description": "Image metadata is stripped. Common for online uploads, messaging apps, and scanners. Not considered tampering on its own.",
            "severity": "INFO",
            "weight": 0,
        })

    # 2. Error Level Analysis (ELA)
    ela_status = ela_result.get("status")
    avg_diff = ela_result.get("average_difference", 0.0)
    anomaly_ratio = ela_result.get("anomaly_ratio_pct", 0.0)
    is_uniform = ela_result.get("is_uniform_compression", False)
    has_high_ela = False

    if is_uniform:
        # Re-compression error is globally uniform across the entire document.
        # DO NOT add tampering points; this is genuine negative evidence for localized splicing!
        discounts += 4.0
        indicators.append({
            "code": "UNIFORM_COMPRESSION",
            "title": "Global Re-compression Detected (Normal)",
            "description": f"Elevated compression error (avg delta: {avg_diff}) is distributed uniformly across the entire page with low spatial variance. Consistent with social media transmission, screenshotting, or multi-generation JPEG saves rather than localized tampering.",
            "severity": "INFO",
            "weight": 0,
        })
    elif ela_status == "HIGH_ANOMALY":
        pts = 35.0 * w_ela
        positive_score += pts
        has_high_ela = True
        indicators.append({
            "code": "HIGH_ELA_ANOMALY",
            "title": "Severe Localized Compression Discrepancy",
            "description": f"ELA detected high localized compression differences (avg diff: {avg_diff}, anomaly area: {anomaly_ratio}%). Spliced or pasted regions exhibit distinct compression boundaries.",
            "severity": "CRITICAL",
            "weight": round(pts, 1),
        })
    elif ela_status == "MODERATE_ANOMALY":
        pts = 16.0 * w_ela
        positive_score += pts
        indicators.append({
            "code": "MODERATE_ELA_ANOMALY",
            "title": "Moderate Error-Level Inconsistency",
            "description": f"Compression delta is moderately elevated in localized regions (avg diff: {avg_diff}). Possible retouching or pasted elements.",
            "severity": "WARNING",
            "weight": round(pts, 1),
        })
    else:
        discounts += 6.0
        indicators.append({
            "code": "UNIFORM_COMPRESSION",
            "title": "Consistent Error-Level Compression",
            "description": f"Uniform compression levels observed across document surfaces (avg diff: {avg_diff}).",
            "severity": "VERIFIED",
            "weight": -6,
        })

    # 3. Noise Splicing Patterns (with Spatial Clustering)
    has_noise_tamper = False
    if noise_result.get("anomaly_detected"):
        pts = 22.0 * w_noise
        positive_score += pts
        has_noise_tamper = True
        cluster_size = noise_result.get("max_cluster_size", 0)
        indicators.append({
            "code": "NOISE_VARIANCE_ANOMALY",
            "title": "Inconsistent Noise / Splicing Patterns",
            "description": f"Identified a contiguous spatial cluster ({cluster_size} tiles) of anomalous noise variance. Suggests elements were digitally spliced from external sources.",
            "severity": "WARNING",
            "weight": round(pts, 1),
        })
    else:
        discounts += 5.0

    # 4. Copy-Move Duplication
    has_copy_move = False
    if copy_move_result.get("detected"):
        pts = 26.0 * w_copy
        positive_score += pts
        has_copy_move = True
        indicators.append({
            "code": "COPY_MOVE_DETECTED",
            "title": "Duplicated Feature / Stamp Patterns",
            "description": copy_move_result.get("description", "Identical visual features were detected across different document coordinates."),
            "severity": "CRITICAL",
            "weight": round(pts, 1),
        })
    else:
        discounts += 4.0

    # 5. Font & Text Layout Inconsistencies
    has_layout_tamper = False
    if layout_result and layout_result.get("inconsistency_detected"):
        pts = 16.0 * w_layout
        positive_score += pts
        has_layout_tamper = True
        indicators.append({
            "code": "TEXT_LAYOUT_INCONSISTENCY",
            "title": "Text Layout / Font Height Inconsistencies",
            "description": layout_result.get("description", "Abnormal word height or baseline jitter detected inside text lines."),
            "severity": "WARNING",
            "weight": round(pts, 1),
        })
    else:
        discounts += 4.0

    # 6. Algorithmic Validation Flags (Checksum Failures, ID Formats)
    has_validation_failure = False
    if validation_flags:
        for flag in validation_flags:
            flag_weight = flag.get("weight", 15) * w_valid
            positive_score += flag_weight
            indicators.append(flag)
            if flag.get("severity") in ("CRITICAL", "HIGH"):
                has_validation_failure = True
    else:
        discounts += 5.0

    # 7. Deep Learning Visual Tampering Signal
    has_ml_tamper = False
    if ml_result and ml_result.get("available"):
        prob_forged = ml_result.get("class_probabilities", {}).get("forged", 0.0)
        pred = ml_result.get("prediction", "genuine")
        if pred == "forged" and prob_forged >= 0.70:
            has_ml_tamper = True
            pts = 26.0
            positive_score += pts
            indicators.append({
                "code": "DEEP_LEARNING_FORGERY_DETECTED",
                "title": "Deep Learning Vision Tampering Signal",
                "description": f"Neural vision model ({ml_result.get('model_architecture', 'CNN')}) flagged document as forged with {prob_forged*100:.1f}% probability.",
                "severity": "CRITICAL" if prob_forged >= 0.85 else "HIGH",
                "weight": pts,
            })
        elif pred == "genuine" and prob_forged < 0.20:
            discounts += 5.0

    # Count independent corroborating tampering signals
    tampering_signals = sum([
        has_critical_software,
        has_high_ela,
        has_noise_tamper,
        has_copy_move,
        has_layout_tamper,
        has_validation_failure,
        has_ml_tamper,
    ])

    # Genuine evidence discounts are scaled:
    # Full discounts apply to genuine documents to keep scores low (<= 25).
    # When multiple tampering signals are corroborated (>= 2), discounts for untouched areas do NOT dilute the tampering score.
    discount_factor = max(0.0, 1.0 - 0.5 * tampering_signals)
    effective_discounts = discounts * discount_factor

    # Calculate Raw Composite Score
    raw_score = max(0.0, positive_score - effective_discounts)
    bounded_score = min(100.0, max(0.0, raw_score))

    # Realistic Confidence Score (0-100%)
    base_confidence = cat_cfg.get("base_confidence", 88.0)
    w = (image_props or {}).get("width", 1000)
    h = (image_props or {}).get("height", 800)

    if w < 700 or h < 500:
        base_confidence -= 14.0
    if is_uniform:
        base_confidence -= 4.0
    if metadata_result.get("has_exif"):
        base_confidence += 5.0

    confidence_score = round(min(96.0, max(40.0, base_confidence)), 1)

    # Multi-Signal Corroboration & Safety Fallback Rules:
    # Rule 1: An isolated signal alone CANNOT classify a document as forged.
    # Requires at least 2 independent corroborating tampering signals.
    if tampering_signals < 2:
        if bounded_score > 54.0:
            bounded_score = 54.0

    # Rule 2: Low confidence (< 60%) or conflicting signals fall back to Needs Manual Review
    if confidence_score < 60.0:
        if bounded_score > 58.0:
            bounded_score = 58.0

    # 3-Tier Status Determination
    genuine_max = thresholds.get("genuine_max", 28)
    forged_min = thresholds.get("forged_min", 65)

    if bounded_score >= forged_min and tampering_signals >= 2 and confidence_score >= 60.0:
        status_3tier = "Likely Forged"
        classification = "LIKELY_FORGED"
        risk_level = "HIGH"
        verdict = "High Risk: Document exhibits multiple corroborated signatures of digital manipulation or tampering."
    elif bounded_score <= genuine_max:
        status_3tier = "Likely Genuine"
        classification = "AUTHENTIC"
        risk_level = "LOW"
        verdict = "Low Risk: Document passes primary forensic consistency, checksum, and metadata checks."
    else:
        status_3tier = "Needs Manual Review"
        classification = "NEEDS_MANUAL_REVIEW"
        risk_level = "MODERATE"
        verdict = "Needs Manual Review: Ambiguous, isolated, or inconclusive anomalies detected. Manual review recommended."

    # Plain-language explanation
    explanation_parts = []
    if status_3tier == "Likely Forged":
        reasons = []
        if has_critical_software:
            reasons.append("editing software binary traces")
        if has_high_ela:
            reasons.append("severe localized compression discrepancies")
        if has_noise_tamper:
            reasons.append("contiguous noise variance splicing clusters")
        if has_copy_move:
            reasons.append("duplicated visual pattern clusters")
        if has_layout_tamper:
            reasons.append("mismatched word heights / baseline offsets")
        if has_validation_failure:
            reasons.append("document identifier checksum failures")
        explanation_parts.append(f"The document exhibits {len(reasons)} corroborated tampering indicators: {', '.join(reasons)}.")
    elif status_3tier == "Needs Manual Review":
        if tampering_signals == 1:
            explanation_parts.append("An isolated anomaly was detected without secondary corroboration. Document exhibits partial inconsistencies that require human inspection.")
        elif confidence_score < 60.0:
            explanation_parts.append("Resolution or compression limits forensic certainty. Automated checks are inconclusive.")
        else:
            explanation_parts.append("Slight compression or texture variations were observed. Inconclusive between natural scanning/compression artifacts and subtle retouching.")
    else:
        explanation_parts.append("The document exhibits uniform pixel error levels, natural texture grain, consistent text layout, and no evidence of digital splicing.")

    explanation = " ".join(explanation_parts)

    limitations = (
        "Automated forensic analysis is probabilistic and based on image pixel variance, compression physics, "
        "and metadata signatures. Social media recompression, multiple camera saves, or physical scanner enhancement "
        "can influence error metrics. This analysis should be used as an investigative tool, not as sole legal proof."
    )

    final_score_int = int(round(bounded_score))

    return {
        "score": final_score_int,
        "risk_score": final_score_int,
        "classification": classification,
        "authenticity_status": status_3tier,
        "authenticity_tier": classification,
        "standard_category": standard_cat,
        "risk_level": risk_level,
        "confidence_score": confidence_score,
        "verdict": verdict,
        "explanation": explanation,
        "limitations": limitations,
        "indicators": indicators,
        "tampering_signals_count": tampering_signals,
    }


# =========================================================
# MAIN FORENSIC ENTRYPOINT
# =========================================================

def analyze_image(file_path, validation_flags=None, words=None, document_type="Unknown"):
    """
    Comprehensive multi-method document forensic analysis.
    Supports JPEG, PNG, WEBP, TIFF, BMP, and rasterized PDF/DOCX pages.
    """
    image = Image.open(file_path)

    # Standardize category and retrieve category config
    standard_cat = get_standard_category(document_type)
    cat_cfg = get_category_config(standard_cat)

    # Check if image has screenshot aspect ratio
    w, h = image.width, image.height
    aspect_ratio = max(w, h) / max(1, min(w, h))
    is_screenshot = (1.7 < aspect_ratio < 2.3) and (image.format == "PNG" or file_path.lower().endswith(".png"))

    # 1. Image Properties
    image_props = {
        "format": image.format or os.path.splitext(file_path)[1].replace(".", "").upper(),
        "width": w,
        "height": h,
        "mode": image.mode,
        "is_screenshot": is_screenshot,
        "standard_category": standard_cat,
    }

    # 2. Metadata Forensics
    metadata_result = inspect_metadata(image, file_path)
    image_props["has_exif"] = metadata_result["has_exif"]

    # 3. Error Level Analysis (ELA)
    ela_result = perform_ela(image, quality=90, multiplier=15)

    # 4. Noise Inconsistency Analysis
    threshold_mult = cat_cfg.get("noise_threshold_mult", 3.0)
    noise_result = analyze_noise_inconsistency(
        image,
        block_size=32,
        is_screenshot=is_screenshot,
        threshold_multiplier=threshold_mult
    )

    # 5. Copy-Move Duplication Analysis
    copy_move_result = detect_copy_move(image)

    # 6. Text Layout Inconsistency Analysis
    layout_result = detect_text_layout_inconsistencies(words)

    # 7. Deep Learning Inference (if trained model exists)
    ml_result = None
    try:
        from ml_detector import predict_document_ml
        ml_result = predict_document_ml(file_path)
    except Exception:
        pass

    # 8. Composite Forgery Score & 3-Tier Assessment
    composite = calculate_composite_forgery_score(
        ela_result,
        noise_result,
        copy_move_result,
        metadata_result,
        layout_result=layout_result,
        validation_flags=validation_flags,
        document_type=document_type,
        image_props=image_props,
        ml_result=ml_result
    )

    return {
        "image_analysis": image_props,
        "metadata_forensics": metadata_result,
        "ela_analysis": {
            "available": ela_result["available"],
            "average_difference": ela_result["average_difference"],
            "max_difference": ela_result["max_difference"],
            "anomaly_ratio_pct": ela_result["anomaly_ratio_pct"],
            "spatial_variance": ela_result.get("spatial_variance", 0.0),
            "is_uniform_compression": ela_result.get("is_uniform_compression", False),
            "status": ela_result["status"],
            "heatmap_image": ela_result["heatmap_image"],
            "diff_image": ela_result["diff_image"],
        },
        "noise_analysis": {
            "available": noise_result["available"],
            "median_variance": noise_result.get("median_noise_variance"),
            "outlier_blocks": noise_result.get("outlier_blocks_count"),
            "max_cluster_size": noise_result.get("max_cluster_size", 0),
            "has_spatial_cluster": noise_result.get("has_spatial_cluster", False),
            "anomaly_detected": noise_result["anomaly_detected"],
            "noise_map_image": noise_result.get("noise_map_image"),
        },
        "copy_move_analysis": copy_move_result,
        "text_layout_analysis": layout_result,
        "ml_inference": ml_result,
        "risk_score": composite["score"],
        "classification": composite["classification"],
        "authenticity_status": composite["authenticity_status"],
        "authenticity_tier": composite["authenticity_tier"],
        "standard_category": composite["standard_category"],
        "risk_level": composite["risk_level"],
        "confidence_score": composite["confidence_score"],
        "verdict": composite["verdict"],
        "explanation": composite["explanation"],
        "limitations": composite["limitations"],
        "indicators": composite["indicators"],
        "tampering_signals_count": composite["tampering_signals_count"],
    }

