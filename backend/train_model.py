import os
import json
import time
from typing import Dict, Any, List
from PIL import Image

from dataset_manager import load_manifest, resolve_image_path
from forgery_detector import analyze_image, DEFAULT_CONFIG

MODEL_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "model_config.json")


def train_and_calibrate(sample_limit: int = 150):
    """
    Trains and calibrates category-specific weights and thresholds on the training split,
    validates on the validation split, and exports model_config.json.
    """
    print("\n=======================================================")
    print("DOCSHIELD AI: MULTI-SIGNAL MODEL CALIBRATION & TRAINING")
    print("=======================================================\n")

    manifest = load_manifest()
    from intelligence.training import audit
    audit_result = audit(manifest, os.path.join(os.path.dirname(__file__), "..", "dataset"))
    if not audit_result["safe_to_train"]:
        raise ValueError("Dataset failed source-level leakage audit; repair splits before calibration")
    train_set = [r for r in manifest if r["split"] == "train"]
    val_set = [r for r in manifest if r["split"] == "validation"]

    print(f"Loaded {len(manifest)} total records.")
    print(f"Training set: {len(train_set)} | Validation set: {len(val_set)}")

    # Subsample if dataset is very large to keep training prompt and snappy
    if len(train_set) > sample_limit:
        import random
        random.seed(42)
        train_sample = random.sample(train_set, sample_limit)
    else:
        train_sample = train_set

    # Category performance statistics
    category_stats: Dict[str, Dict[str, List[float]]] = {}
    for cat in DEFAULT_CONFIG["categories"].keys():
        category_stats[cat] = {"genuine_scores": [], "forged_scores": []}

    print(f"\nExtracting multi-signal forensic features on {len(train_sample)} training documents...")
    start_time = time.time()

    processed = 0
    for rec in train_sample:
        fpath = resolve_image_path(rec["filename"], split=rec["split"], label=rec["label"])
        if not os.path.exists(fpath):
            continue

        try:
            res = analyze_image(fpath, document_type=rec["document_type"])
            score = float(res.get("risk_score", 0))
            cat = rec["document_type"]

            if cat not in category_stats:
                category_stats[cat] = {"genuine_scores": [], "forged_scores": []}

            if rec["label"] == "genuine":
                category_stats[cat]["genuine_scores"].append(score)
            else:
                category_stats[cat]["forged_scores"].append(score)

            processed += 1
            if processed % 30 == 0:
                print(f"  Processed {processed}/{len(train_sample)} documents...")
        except Exception as e:
            continue

    elapsed = time.time() - start_time
    print(f"Feature extraction completed in {elapsed:.1f}s ({processed} docs processed).\n")

    # Fit calibrated thresholds per category
    calibrated_categories = {}
    for cat, def_cfg in DEFAULT_CONFIG["categories"].items():
        stats = category_stats.get(cat, {"genuine_scores": [], "forged_scores": []})
        g_scores = stats["genuine_scores"]
        f_scores = stats["forged_scores"]

        if g_scores:
            # 95th percentile of genuine scores gives safe upper bound for Likely Genuine
            p95_genuine = float(np.percentile(g_scores, 95)) if len(g_scores) >= 5 else 26.0
            calibrated_genuine_max = int(min(32, max(22, round(p95_genuine))))
        else:
            calibrated_genuine_max = def_cfg["thresholds"]["genuine_max"]

        if f_scores:
            # 10th percentile of forged scores gives safe lower bound for Likely Forged
            p10_forged = float(np.percentile(f_scores, 10)) if len(f_scores) >= 5 else 62.0
            calibrated_forged_min = int(max(60, min(70, round(p10_forged))))
        else:
            calibrated_forged_min = def_cfg["thresholds"]["forged_min"]

        calibrated_categories[cat] = {
            "weights": def_cfg["weights"],
            "thresholds": {
                "genuine_max": calibrated_genuine_max,
                "forged_min": calibrated_forged_min,
            },
            "noise_threshold_mult": def_cfg.get("noise_threshold_mult", 3.0),
            "min_corroborating_signals": 2,
            "training_samples_genuine": len(g_scores),
            "training_samples_forged": len(f_scores),
        }

        print(f"Category '{cat}': genuine_max <= {calibrated_genuine_max}, forged_min >= {calibrated_forged_min} (n_g={len(g_scores)}, n_f={len(f_scores)})")

    model_config = {
        "version": "2.2.0",
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "global": DEFAULT_CONFIG["global"],
        "categories": calibrated_categories,
    }

    with open(MODEL_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(model_config, f, indent=2)

    print(f"\nSaved calibrated model configuration to {MODEL_CONFIG_PATH}")

    # Validation pass
    print("\nRunning validation evaluation...")
    val_sample = val_set[:60] if len(val_set) > 60 else val_set
    val_correct = 0
    val_total = 0

    for rec in val_sample:
        fpath = resolve_image_path(rec["filename"], split=rec["split"], label=rec["label"])
        if not os.path.exists(fpath):
            continue
        try:
            res = analyze_image(fpath, document_type=rec["document_type"])
            pred = res.get("classification")
            label = rec["label"]
            # Genuine should be AUTHENTIC or NEEDS_MANUAL_REVIEW, NOT LIKELY_FORGED
            if label == "genuine" and pred != "LIKELY_FORGED":
                val_correct += 1
            # Forged should be LIKELY_FORGED or NEEDS_MANUAL_REVIEW, NOT AUTHENTIC
            elif label == "forged" and pred != "AUTHENTIC":
                val_correct += 1
            val_total += 1
        except Exception:
            continue

    if val_total > 0:
        val_acc = (val_correct / val_total) * 100.0
        print(f"Validation Safe Accuracy: {val_acc:.1f}% ({val_correct}/{val_total})\n")

    return model_config


if __name__ == "__main__":
    import numpy as np
    train_and_calibrate(sample_limit=100)
