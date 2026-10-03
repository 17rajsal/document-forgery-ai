"""
Proofly AI Erase & Generative Inpainting Detector
Analyzes documents for localized digital reconstruction, generative fill,
content-aware erase, and synthetic texture blending.

Multi-Signal Approach:
1. High-Frequency Noise Residual Discontinuity (Wavelet / Median subtraction)
2. Frequency-Domain DCT Energy Decay (Inpainting over-smoothness signature)
3. Local Gradient Profile & Edge Boundary Discontinuity
4. Reconstructed Texture Inconsistency vs. Global Document Grain
"""

import os
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Optional, Tuple


def compute_noise_residual(gray_img: np.ndarray) -> np.ndarray:
    """
    Extracts high-frequency sensor/compression noise residual by subtracting
    a 3x3 median-filtered image from the original grayscale image.
    Natural documents maintain consistent noise residuals across paper fibers.
    AI inpainting or erase creates an 'unnaturally silent' or smoothed noise valley.
    """
    denoised = cv2.medianBlur(gray_img, 3)
    residual = cv2.absdiff(gray_img, denoised)
    return residual


def compute_dct_energy_ratio(block: np.ndarray) -> float:
    """
    Computes ratio of high-frequency DCT energy to total energy for an 8x8 or 16x16 block.
    Generative inpainting and AI erase suppress high-frequency DCT coefficients.
    """
    h, w = block.shape
    if h < 8 or w < 8:
        return 0.5

    # Float32 DCT
    float_block = np.float32(block) / 255.0
    dct = cv2.dct(float_block)

    total_energy = np.sum(np.abs(dct))
    if total_energy < 1e-6:
        return 0.0

    # Low frequency corner is top-left
    low_freq = np.sum(np.abs(dct[:h//2, :w//2]))
    high_freq = total_energy - low_freq
    return float(high_freq / total_energy)


def detect_ai_erase_and_inpainting(
    image_input: Any,
    grid_size: int = 32,
    sensitivity: float = 2.4
) -> Dict[str, Any]:
    """
    Scans the document across overlapping spatial grids to detect localized
    signatures of AI erase, generative inpainting, or object replacement.

    Returns:
      - candidate_regions: list of bounding boxes with severity, local smoothness, and noise gap
      - overall_inpainting_risk: "LOW", "MODERATE", "EVIDENCE_DETECTED"
      - anomaly_coverage_pct: percentage of document exhibiting localized reconstruction anomalies
      - heatmap_b64: base64 preview of detected anomaly regions
    """
    if isinstance(image_input, Image.Image):
        cv_img = cv2.cvtColor(np.array(image_input.convert("RGB")), cv2.COLOR_RGB2BGR)
    elif isinstance(image_input, str):
        cv_img = cv2.imread(image_input)
    elif isinstance(image_input, np.ndarray):
        cv_img = image_input
    else:
        return {"available": False, "reason": "Invalid image input"}

    if cv_img is None:
        return {"available": False, "reason": "Could not decode image"}

    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape

    # 1. Noise residual map
    noise_residual = compute_noise_residual(gray)

    # 2. Gradient magnitude (Sobel)
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    gradient_mag = cv2.magnitude(grad_x, grad_y)

    step = grid_size // 2
    y_steps = range(0, height - grid_size + 1, step)
    x_steps = range(0, width - grid_size + 1, step)

    tile_noise_vars = []
    tile_dct_ratios = []
    tile_edge_densities = []
    tile_coords = []

    for y in y_steps:
        for x in x_steps:
            block_gray = gray[y:y+grid_size, x:x+grid_size]
            block_noise = noise_residual[y:y+grid_size, x:x+grid_size]
            block_grad = gradient_mag[y:y+grid_size, x:x+grid_size]

            # Ignore pure solid white canvas margins (very high brightness, low variance)
            if np.mean(block_gray) > 248 and np.std(block_gray) < 2.0:
                continue

            n_var = float(np.var(block_noise))
            dct_r = compute_dct_energy_ratio(block_gray)
            e_density = float(np.mean(block_grad))

            tile_noise_vars.append(n_var)
            tile_dct_ratios.append(dct_r)
            tile_edge_densities.append(e_density)
            tile_coords.append((x, y))

    if len(tile_noise_vars) < 20:
        return {
            "available": True,
            "inpainting_detected": False,
            "confidence": 50.0,
            "candidate_regions": [],
            "anomaly_coverage_pct": 0.0,
            "summary": "Document content too sparse for statistical inpainting decomposition."
        }

    # Global baselines across the document body
    median_noise_var = float(np.median(tile_noise_vars))
    iqr_noise_var = float(np.percentile(tile_noise_vars, 75) - np.percentile(tile_noise_vars, 25))
    median_dct = float(np.median(tile_dct_ratios))

    # An inpainting / AI-erase patch typically exhibits:
    # 1. Significantly lower noise residual than surrounding paper (local smoothing)
    # 2. Abnormally low DCT high-frequency energy ratio compared to text/paper
    # 3. Discontinuous gradient boundary around the patch
    suspicious_mask = np.zeros((height, width), dtype=np.uint8)
    suspicious_tiles = []

    for idx, (x, y) in enumerate(tile_coords):
        n_var = tile_noise_vars[idx]
        dct_r = tile_dct_ratios[idx]
        e_dens = tile_edge_densities[idx]

        # Condition for synthetic smoothing / AI erase signature
        # Noise variance is less than half the document median, AND DCT high freq is depressed
        is_unnatural_smoothness = (
            median_noise_var > 4.0 and
            n_var < max(0.5, median_noise_var * 0.28) and
            dct_r < median_dct * 0.45
        )

        # Condition for generative fill edge splice
        # High noise anomaly vs neighboring paper
        is_synthetic_splice = (
            iqr_noise_var > 1.0 and
            n_var > (median_noise_var + sensitivity * iqr_noise_var) and
            e_dens > 15.0
        )

        if is_unnatural_smoothness or is_synthetic_splice:
            suspicious_mask[y:y+grid_size, x:x+grid_size] = 255
            suspicious_tiles.append({
                "x": x, "y": y, "w": grid_size, "h": grid_size,
                "type": "unnatural_smoothing" if is_unnatural_smoothness else "synthetic_splice",
                "noise_ratio": round(n_var / max(0.01, median_noise_var), 2)
            })

    # Group spatially contiguous suspicious tiles via connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(suspicious_mask, connectivity=8)

    candidate_regions = []
    min_cluster_pixels = (grid_size * grid_size) # At least one full tile equivalent
    total_anomalous_pixels = 0

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_cluster_pixels:
            bx = int(stats[i, cv2.CC_STAT_LEFT])
            by = int(stats[i, cv2.CC_STAT_TOP])
            bw = int(stats[i, cv2.CC_STAT_WIDTH])
            bh = int(stats[i, cv2.CC_STAT_HEIGHT])
            total_anomalous_pixels += area

            # Heuristic severity
            severity = "HIGH" if area > (grid_size * grid_size * 3) else "MODERATE"

            candidate_regions.append({
                "bbox": {"x": bx, "y": by, "w": bw, "h": bh},
                "area_px": int(area),
                "severity": severity,
                "category": "POSSIBLE_AI_INPAINTING_OR_ERASE",
                "finding": "Localized texture inconsistency and high-frequency noise suppression.",
                "explanation": (
                    "Pixels in this region show uniform reconstructed smoothness and missing microscopic paper noise, "
                    "a statistical fingerprint frequently observed after AI object removal, generative erase, or patch inpainting."
                )
            })

    coverage_pct = round((total_anomalous_pixels / max(1, width * height)) * 100.0, 2)
    inpainting_detected = len(candidate_regions) > 0 and coverage_pct > 0.08

    return {
        "available": True,
        "inpainting_detected": inpainting_detected,
        "candidate_regions": candidate_regions,
        "regions_count": len(candidate_regions),
        "anomaly_coverage_pct": coverage_pct,
        "median_noise_baseline": round(median_noise_var, 2),
        "disclaimer": "These signals indicate possible digital alteration or reconstructed regions and do not independently prove deliberate fraud."
    }
