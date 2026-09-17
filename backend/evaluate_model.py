import os
import sys
import json
import time
from typing import Dict, Any, List

from dataset_manager import load_manifest, resolve_image_path
from forgery_detector import analyze_image


def evaluate(test_limit: int = 140) -> Dict[str, Any]:
    """
    Evaluates the multi-signal forgery detection model on the held-out test split.
    Reports Precision, Recall, F1, Confusion Matrix, FPR, FNR, and breakdown by document category.
    """
    print("\n=======================================================")
    print("DOCSHIELD AI: FORENSIC MODEL COMPREHENSIVE EVALUATION")
    print("=======================================================\n")

    manifest = load_manifest()
    test_set = [r for r in manifest if r.get("split") == "test"]

    if not test_set:
        print("Warning: No test split found in manifest, using validation/test records...")
        test_set = [r for r in manifest if r.get("split") in ("test", "validation")]

    if test_limit and len(test_set) > test_limit:
        test_set = test_set[:test_limit]

    print(f"Evaluating on {len(test_set)} test documents...\n")

    # Global counters
    tp = 0  # Forged predicted as Likely Forged
    fp = 0  # Genuine predicted as Likely Forged (CRITICAL FALSE POSITIVE)
    tn = 0  # Genuine predicted as Likely Genuine
    fn = 0  # Forged predicted as Likely Genuine (CRITICAL FALSE NEGATIVE)
    mr_genuine = 0  # Genuine routed to Manual Review
    mr_forged = 0   # Forged routed to Manual Review

    # Category breakdown: cat -> {tp, fp, tn, fn, mr_g, mr_f, total}
    cat_metrics: Dict[str, Dict[str, int]] = {}

    start_time = time.time()
    evaluated_count = 0

    for idx, rec in enumerate(test_set, 1):
        fpath = resolve_image_path(rec["filename"], split=rec.get("split", ""), label=rec.get("label", ""))
        if not os.path.exists(fpath):
            continue

        cat = rec.get("document_type", "general_scanned")
        if cat not in cat_metrics:
            cat_metrics[cat] = {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "mr_g": 0, "mr_f": 0, "total": 0}

        true_label = rec["label"].lower()  # "genuine" or "forged"

        try:
            res = analyze_image(fpath, document_type=cat)
            pred_status = res.get("authenticity_status", "Likely Genuine")
            # pred_status is one of: "Likely Genuine", "Needs Manual Review", "Likely Forged"

            cat_metrics[cat]["total"] += 1
            evaluated_count += 1

            if true_label == "forged":
                if pred_status == "Likely Forged":
                    tp += 1
                    cat_metrics[cat]["tp"] += 1
                elif pred_status == "Needs Manual Review":
                    mr_forged += 1
                    cat_metrics[cat]["mr_f"] += 1
                else:  # Likely Genuine
                    fn += 1
                    cat_metrics[cat]["fn"] += 1
            else:  # true_label == "genuine"
                if pred_status == "Likely Genuine":
                    tn += 1
                    cat_metrics[cat]["tn"] += 1
                elif pred_status == "Needs Manual Review":
                    mr_genuine += 1
                    cat_metrics[cat]["mr_g"] += 1
                else:  # Likely Forged
                    fp += 1
                    cat_metrics[cat]["fp"] += 1

            if idx % 25 == 0:
                print(f"  Evaluated {idx}/{len(test_set)} documents...")
        except Exception as e:
            continue

    elapsed = time.time() - start_time
    print(f"\nEvaluation completed in {elapsed:.1f}s ({evaluated_count} documents evaluated).\n")

    # Mathematical metric computations
    # In safety-critical forensics, Manual Review is an investigative hold (inconclusive).
    # Precision of positive alerts: TP / (TP + FP)
    precision = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
    # Recall of affirmative forgeries: TP / (TP + FN)
    recall = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
    # Effective recall (including those caught and flagged for manual inspection)
    catch_rate = ((tp + mr_forged) / max(1, tp + mr_forged + fn)) * 100.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    # False Positive Rate (genuine docs incorrectly declared Likely Forged):
    total_genuine = tn + fp + mr_genuine
    fpr = (fp / max(1, total_genuine)) * 100.0

    # False Negative Rate (forged docs incorrectly declared Likely Genuine):
    total_forged = tp + fn + mr_forged
    fnr = (fn / max(1, total_forged)) * 100.0

    # Overall Manual Review Rate
    total_docs = max(1, evaluated_count)
    manual_review_rate = ((mr_genuine + mr_forged) / total_docs) * 100.0

    print("-------------------------------------------------------------------")
    print("GLOBAL PERFORMANCE METRICS")
    print("-------------------------------------------------------------------")
    print(f"Total Test Documents:          {evaluated_count}")
    print(f"Precision (Likely Forged):     {precision:.2f}%")
    print(f"Recall (Likely Forged):        {recall:.2f}%")
    print(f"F1 Score:                      {f1:.2f}%")
    print(f"False Positive Rate (FPR):     {fpr:.2f}%  (Target <= 5.0%)")
    print(f"False Negative Rate (FNR):     {fnr:.2f}%")
    print(f"Forgery Catch Rate (Forged+MR):{catch_rate:.2f}%")
    print(f"Manual Review Rate:            {manual_review_rate:.2f}%")
    print("-------------------------------------------------------------------")
    print("\nCONFUSION MATRIX:")
    print("                       Predicted Genuine   Predicted Review   Predicted Forged")
    print(f"  Actual Genuine:     {tn:<19} {mr_genuine:<18} {fp:<16}")
    print(f"  Actual Forged:      {fn:<19} {mr_forged:<18} {tp:<16}")
    print("-------------------------------------------------------------------\n")

    print("CATEGORY BREAKDOWN:")
    print(f"{'Category':<20} | {'Total':<6} | {'TN':<4} | {'FP':<4} | {'FN':<4} | {'TP':<4} | {'MR_G':<5} | {'MR_F':<5} | {'FPR':<6}")
    print("-" * 75)

    category_results = {}
    for cat, m in cat_metrics.items():
        cat_g = m["tn"] + m["fp"] + m["mr_g"]
        cat_fpr = (m["fp"] / max(1, cat_g)) * 100.0
        cat_f = m["tp"] + m["fn"] + m["mr_f"]
        cat_fnr = (m["fn"] / max(1, cat_f)) * 100.0
        print(f"{cat:<20} | {m['total']:<6} | {m['tn']:<4} | {m['fp']:<4} | {m['fn']:<4} | {m['tp']:<4} | {m['mr_g']:<5} | {m['mr_f']:<5} | {cat_fpr:.1f}%")
        category_results[cat] = {
            "total": m["total"],
            "tn": m["tn"],
            "fp": m["fp"],
            "fn": m["fn"],
            "tp": m["tp"],
            "mr_genuine": m["mr_g"],
            "mr_forged": m["mr_f"],
            "fpr": round(cat_fpr, 2),
            "fnr": round(cat_fnr, 2),
        }

    print("-------------------------------------------------------------------\n")

    return {
        "total_evaluated": evaluated_count,
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1": round(f1, 2),
        "fpr": round(fpr, 2),
        "fnr": round(fnr, 2),
        "forgery_catch_rate": round(catch_rate, 2),
        "manual_review_rate": round(manual_review_rate, 2),
        "confusion_matrix": {
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "mr_genuine": mr_genuine,
            "mr_forged": mr_forged,
        },
        "category_breakdown": category_results,
    }


if __name__ == "__main__":
    evaluate(test_limit=140)
