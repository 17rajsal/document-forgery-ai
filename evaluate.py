import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

from train import DocumentImageFolder, build_model, IMAGE_SIZE, CLASS_TO_IDX, IDX_TO_CLASS

DATASET_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "dataset"))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))
OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "outputs"))

MODEL_PATH = os.path.join(MODELS_DIR, "document_forgery_model.pth")
TRAIN_HISTORY_PATH = os.path.join(OUTPUTS_DIR, "training_history.json")

EVAL_RESULTS_PATH = os.path.join(OUTPUTS_DIR, "evaluation_results.json")
REPORT_PATH = os.path.join(OUTPUTS_DIR, "classification_report.txt")
CONFUSION_MATRIX_PATH = os.path.join(OUTPUTS_DIR, "confusion_matrix.png")
TRAINING_CURVES_PATH = os.path.join(OUTPUTS_DIR, "training_curves.png")


def plot_confusion_matrix(cm: np.ndarray, classes: List[str], save_path: str):
    """Generates an annotated confusion matrix plot using matplotlib."""
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.figure.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes,
        yticklabels=classes,
        title="Document Forgery AI - Test Confusion Matrix",
        ylabel="True Ground Truth Label",
        xlabel="Predicted Label",
    )

    # Text annotations inside matrix cells
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            count = cm[i, j]
            pct = (count / cm[i].sum()) * 100.0 if cm[i].sum() > 0 else 0.0
            ax.text(
                j, i,
                f"{count}\n({pct:.1f}%)",
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "#0f172a",
                fontsize=11, weight="bold"
            )

    fig.tight_layout()
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[*] Confusion matrix plot saved to {save_path}")


def plot_training_curves(history: Dict[str, Any], save_path: str):
    """Generates loss and accuracy curves across training epochs."""
    epochs_data = history.get("epochs", [])
    if not epochs_data:
        print("[!] No epoch history to plot.")
        return

    epochs = [e["epoch"] for e in epochs_data]
    train_loss = [e["train"]["loss"] for e in epochs_data]
    val_loss = [e["validation"]["loss"] for e in epochs_data]

    train_acc = [e["train"]["accuracy"] for e in epochs_data]
    val_acc = [e["validation"]["accuracy"] for e in epochs_data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=150)

    # Loss Curve
    ax1.plot(epochs, train_loss, "o-", label="Train Loss", color="#2563eb", linewidth=2)
    ax1.plot(epochs, val_loss, "s--", label="Val Loss", color="#dc2626", linewidth=2)
    ax1.set_title("Training & Validation Loss")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Weighted Cross-Entropy Loss")
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend()

    # Accuracy Curve
    ax2.plot(epochs, train_acc, "o-", label="Train Accuracy (%)", color="#2563eb", linewidth=2)
    ax2.plot(epochs, val_acc, "s--", label="Val Accuracy (%)", color="#16a34a", linewidth=2)
    ax2.set_title("Training & Validation Accuracy")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy (%)")
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend()

    fig.tight_layout()
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[*] Training curves plot saved to {save_path}")


def evaluate(args):
    # 1. Device selection
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        device_name = f"CUDA/GPU ({torch.cuda.get_device_name(0)})"
    else:
        device = torch.device("cpu")
        device_name = "CPU"
        torch.set_num_threads(os.cpu_count() or 4)

    print("\n=============================================================")
    print("DOCSHIELD AI: UNSEEN TEST DATASET EVALUATION")
    print("=============================================================")
    print(f"Selected Device: {device_name}")
    print(f"Model Checkpoint: {MODEL_PATH}")
    print("=============================================================\n")

    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model checkpoint not found at '{MODEL_PATH}'! Train the model first.")
        sys.exit(1)

    # 2. Load Checkpoint
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    arch = checkpoint.get("arch", "mobilenet_v3_small")
    model = build_model(arch=arch, pretrained=False).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    print(f"[*] Successfully loaded trained {arch} model checkpoint (Best Epoch: {checkpoint.get('best_epoch', 'N/A')}).")

    # 3. Load Test Dataset
    eval_transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    test_dir = os.path.join(DATASET_ROOT, "test")
    test_dataset = DocumentImageFolder(test_dir, transform=eval_transform)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)

    print(f"[*] Loaded unseen test dataset: {len(test_dataset)} images.")

    # 4. Run Inference on Test Dataset
    all_preds = []
    all_targets = []
    all_probs = []

    start_eval = time.time()
    with torch.no_grad():
        for images, targets in test_loader:
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(probs, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.numpy())
            all_probs.extend(probs.cpu().numpy()[:, 1])  # Forged probability

    eval_duration = time.time() - start_eval
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)

    # 5. Compute Metrics
    total_test = len(all_targets)
    correct_count = int((all_preds == all_targets).sum())
    incorrect_count = int((all_preds != all_targets).sum())

    acc = float(accuracy_score(all_targets, all_preds)) * 100.0
    prec = float(precision_score(all_targets, all_preds, average="binary", zero_division=0)) * 100.0
    rec = float(recall_score(all_targets, all_preds, average="binary", zero_division=0)) * 100.0
    f1 = float(f1_score(all_targets, all_preds, average="binary", zero_division=0)) * 100.0

    # Per-class metrics
    # Genuine class (0)
    prec_genuine = float(precision_score(all_targets == 0, all_preds == 0, zero_division=0)) * 100.0
    rec_genuine = float(recall_score(all_targets == 0, all_preds == 0, zero_division=0)) * 100.0
    f1_genuine = float(f1_score(all_targets == 0, all_preds == 0, zero_division=0)) * 100.0

    # Forged class (1)
    prec_forged = prec
    rec_forged = rec
    f1_forged = f1

    # Confusion Matrix
    cm = confusion_matrix(all_targets, all_preds)
    tn, fp, fn, tp = cm.ravel()

    # Classification Report Text
    target_names = ["genuine (0)", "forged (1)"]
    report_text = classification_report(all_targets, all_preds, target_names=target_names, digits=4)

    print("-------------------------------------------------------------")
    print("UNSEEN TEST SET PERFORMANCE METRICS")
    print("-------------------------------------------------------------")
    print(f"Total Test Images:               {total_test}")
    print(f"Correct Predictions:             {correct_count} ({correct_count/total_test*100:.2f}%)")
    print(f"Incorrect Predictions:           {incorrect_count} ({incorrect_count/total_test*100:.2f}%)")
    print(f"Test Accuracy:                   {acc:.2f}%")
    print(f"Test Precision:                  {prec:.2f}%")
    print(f"Test Recall:                     {rec:.2f}%")
    print(f"Test F1-Score:                   {f1:.2f}%")
    print("-------------------------------------------------------------")
    print("PER-CLASS METRICS:")
    print(f"  Genuine Class (0) -> Precision: {prec_genuine:.2f}%, Recall: {rec_genuine:.2f}%, F1: {f1_genuine:.2f}%")
    print(f"  Forged Class (1)  -> Precision: {prec_forged:.2f}%, Recall: {rec_forged:.2f}%, F1: {f1_forged:.2f}%")
    print("-------------------------------------------------------------")
    print("CONFUSION MATRIX:")
    print(f"  True Negatives (Genuine identified as Genuine): {tn}")
    print(f"  False Positives (Genuine identified as Forged):  {fp}")
    print(f"  False Negatives (Forged missed as Genuine):     {fn}")
    print(f"  True Positives (Forged correctly caught):       {tp}")
    print("-------------------------------------------------------------\n")
    print("CLASSIFICATION REPORT:")
    print(report_text)

    # 6. Overfitting Analysis
    training_history = {}
    overfitting_analysis = {
        "overfitting_detected": False,
        "gap_percentage_points": 0.0,
        "notes": []
    }

    if os.path.exists(TRAIN_HISTORY_PATH):
        try:
            with open(TRAIN_HISTORY_PATH, "r", encoding="utf-8") as f:
                training_history = json.load(f)

            best_ep = checkpoint.get("best_epoch", 1)
            epochs_list = training_history.get("epochs", [])
            best_epoch_data = next((e for e in epochs_list if e["epoch"] == best_ep), None)

            if best_epoch_data:
                train_acc_best = best_epoch_data["train"]["accuracy"]
                val_acc_best = best_epoch_data["validation"]["accuracy"]
                gap = train_acc_best - acc
                overfitting_analysis["train_accuracy"] = train_acc_best
                overfitting_analysis["val_accuracy"] = val_acc_best
                overfitting_analysis["test_accuracy"] = acc
                overfitting_analysis["gap_percentage_points"] = round(gap, 2)

                print("-------------------------------------------------------------")
                print("OVERFITTING & GENERALIZATION ANALYSIS")
                print("-------------------------------------------------------------")
                print(f"Best Epoch ({best_ep}) Train Accuracy: {train_acc_best:.2f}%")
                print(f"Best Epoch ({best_ep}) Val Accuracy:   {val_acc_best:.2f}%")
                print(f"Unseen Test Accuracy:            {acc:.2f}%")
                print(f"Train-to-Test Gap:               {gap:+.2f} percentage points")

                if gap > 8.0:
                    overfitting_analysis["overfitting_detected"] = True
                    msg = f"Overfitting flag: Training accuracy exceeds test accuracy by {gap:.2f}% (> 8.0% benchmark)."
                    overfitting_analysis["notes"].append(msg)
                    print(f"[!] {msg}")
                else:
                    msg = f"Well-generalized: Train-to-test accuracy gap ({gap:.2f}%) is within standard acceptable bounds."
                    overfitting_analysis["notes"].append(msg)
                    print(f"[*] {msg}")

                if rec_forged < 85.0:
                    warn = f"Notice: Forged-class recall is {rec_forged:.2f}% (benchmark: ~85%). The model should be paired with multi-spectrum ELA and OCR layout heuristics."
                    overfitting_analysis["notes"].append(warn)
                    print(f"[!] {warn}")

                print("-------------------------------------------------------------\n")
        except Exception as e:
            print(f"Could not parse training history for overfitting analysis: {e}")

    # 7. Save outputs
    eval_results = {
        "model_path": MODEL_PATH,
        "selected_device": device_name,
        "architecture": arch,
        "class_mapping": CLASS_TO_IDX,
        "image_size": list(IMAGE_SIZE),
        "total_test_images": total_test,
        "evaluation_duration_seconds": round(eval_duration, 2),
        "metrics": {
            "accuracy": round(acc, 2),
            "precision": round(prec, 2),
            "recall": round(rec, 2),
            "f1_score": round(f1, 2),
            "correct_predictions": correct_count,
            "incorrect_predictions": incorrect_count,
            "per_class": {
                "genuine": {
                    "precision": round(prec_genuine, 2),
                    "recall": round(rec_genuine, 2),
                    "f1_score": round(f1_genuine, 2),
                    "support": int((all_targets == 0).sum()),
                },
                "forged": {
                    "precision": round(prec_forged, 2),
                    "recall": round(rec_forged, 2),
                    "f1_score": round(f1_forged, 2),
                    "support": int((all_targets == 1).sum()),
                }
            }
        },
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
        "overfitting_analysis": overfitting_analysis,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(EVAL_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)
    print(f"[*] Evaluation results saved to {EVAL_RESULTS_PATH}")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"[*] Classification report saved to {REPORT_PATH}")

    # Save visual charts
    plot_confusion_matrix(cm, classes=["genuine", "forged"], save_path=CONFUSION_MATRIX_PATH)
    if training_history:
        plot_training_curves(training_history, save_path=TRAINING_CURVES_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Document Forgery Model on Unseen Test Split")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for evaluation")
    args = parser.parse_args()
    evaluate(args)
