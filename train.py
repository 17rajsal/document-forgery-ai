import os
import sys
import time
import json
import argparse
from typing import Tuple, Dict, Any, List

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

# =========================================================
# CONFIGURATION & CONSTANTS
# =========================================================

DATASET_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "dataset"))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))
OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "outputs"))

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

MODEL_SAVE_PATH = os.path.join(MODELS_DIR, "document_forgery_model.pth")
TRAIN_HISTORY_PATH = os.path.join(OUTPUTS_DIR, "training_history.json")

CLASS_TO_IDX = {"genuine": 0, "forged": 1}
IDX_TO_CLASS = {0: "genuine", 1: "forged"}
IMAGE_SIZE = (224, 224)


# =========================================================
# DATASET LOADER WITH STRICT CLASS MAPPING
# =========================================================

class DocumentImageFolder(datasets.ImageFolder):
    """
    Ensures binary mapping is strictly genuine=0, forged=1,
    overriding default alphabetical sorting.
    """
    def find_classes(self, directory: str):
        classes = ["genuine", "forged"]
        class_to_idx = {"genuine": 0, "forged": 1}
        # Verify subdirectories exist
        for c in classes:
            cdir = os.path.join(directory, c)
            if not os.path.isdir(cdir):
                raise FileNotFoundError(f"Expected class subdirectory '{c}' in '{directory}'")
        return classes, class_to_idx


def get_data_transforms() -> Tuple[transforms.Compose, transforms.Compose]:
    """
    Moderate, safe data augmentations that preserve localized forgery artifacts.
    """
    train_transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=3),
        transforms.ColorJitter(brightness=0.06, contrast=0.06),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    eval_transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    return train_transform, eval_transform


# =========================================================
# MODEL ARCHITECTURE BUILDER
# =========================================================

def build_model(arch: str = "mobilenet_v3_small", pretrained: bool = True) -> nn.Module:
    """
    Constructs a lightweight transfer learning model (MobileNetV3 or ResNet18)
    adapted for binary document forgery classification.
    """
    if arch == "mobilenet_v3_small":
        weights = models.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
        model = models.mobilenet_v3_small(weights=weights)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(in_features, 2)
    elif arch == "resnet18":
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, 2)
    else:
        raise ValueError(f"Unsupported architecture '{arch}'. Choose 'mobilenet_v3_small' or 'resnet18'.")

    return model


# =========================================================
# SANITY CHECK
# =========================================================

def run_sanity_check(
    train_dataset: DocumentImageFolder,
    val_dataset: DocumentImageFolder,
    model: nn.Module,
    criterion: nn.Module,
    device: torch.device
):
    """
    Pre-training verification suite as required by Rule 12:
    - Verify image loading
    - Verify both classes are present
    - Verify label mapping (genuine=0, forged=1)
    - Verify model forward pass and output shapes
    - Verify loss calculation
    - Verify one short training step with backward pass
    """
    print("\n-------------------------------------------------------------")
    print("RUNNING PRE-TRAINING SANITY CHECK")
    print("-------------------------------------------------------------")

    # 1. Image loading & dataset verification
    print(f"[*] Train dataset samples: {len(train_dataset)}")
    print(f"[*] Validation dataset samples: {len(val_dataset)}")
    assert len(train_dataset) > 0, "Train dataset is empty!"
    assert len(val_dataset) > 0, "Validation dataset is empty!"

    # 2. Class mapping verification
    print(f"[*] Class to index mapping: {train_dataset.class_to_idx}")
    assert train_dataset.class_to_idx == {"genuine": 0, "forged": 1}, (
        f"Invalid mapping: {train_dataset.class_to_idx}. Must be genuine=0, forged=1."
    )
    assert val_dataset.class_to_idx == {"genuine": 0, "forged": 1}, "Validation mapping mismatch!"

    # Count samples per class in train set
    train_targets = [sample[1] for sample in train_dataset.samples]
    genuine_count = train_targets.count(0)
    forged_count = train_targets.count(1)
    print(f"[*] Train class distribution: Genuine (0)={genuine_count}, Forged (1)={forged_count}")
    assert genuine_count > 0, "No genuine images in training set!"
    assert forged_count > 0, "No forged images in training set!"

    # 3. Model forward pass and loss check
    model.train()
    loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    images, labels = next(iter(loader))
    images, labels = images.to(device), labels.to(device)

    print(f"[*] Batch image tensor shape: {images.shape}")
    print(f"[*] Batch label tensor: {labels.tolist()}")
    assert images.shape == (4, 3, 224, 224), f"Unexpected tensor shape: {images.shape}"

    outputs = model(images)
    print(f"[*] Forward pass logits shape: {outputs.shape}")
    assert outputs.shape == (4, 2), f"Expected shape (4, 2), got {outputs.shape}"

    loss = criterion(outputs, labels)
    loss_val = loss.item()
    print(f"[*] Loss computation: {loss_val:.4f}")
    assert not torch.isnan(loss), "Loss computed as NaN!"
    assert not torch.isinf(loss), "Loss computed as Inf!"

    # 4. Backward pass & optimizer step
    optimizer = optim.AdamW(model.parameters(), lr=0.001)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    print("[*] Backward pass & gradient update verified successfully.")

    print("-------------------------------------------------------------")
    print("[PASS] SANITY CHECK COMPLETED: All verification checks passed!")
    print("-------------------------------------------------------------\n")


# =========================================================
# EVALUATION HELPER (VAL / TEST)
# =========================================================

def evaluate_loader(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> Dict[str, float]:
    """
    Evaluates model on a DataLoader, returning loss, accuracy, precision, recall, and F1.
    """
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for images, targets in loader:
            images = images.to(device)
            targets = targets.to(device)

            outputs = model(images)
            loss = criterion(outputs, targets)

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())

    total = len(all_targets)
    epoch_loss = running_loss / max(1, total)

    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)

    acc = float(accuracy_score(all_targets, all_preds))
    prec = float(precision_score(all_targets, all_preds, average="binary", zero_division=0))
    rec = float(recall_score(all_targets, all_preds, average="binary", zero_division=0))
    f1 = float(f1_score(all_targets, all_preds, average="binary", zero_division=0))

    # Per-class metrics
    prec_genuine = float(precision_score(all_targets == 0, all_preds == 0, zero_division=0))
    rec_genuine = float(recall_score(all_targets == 0, all_preds == 0, zero_division=0))
    f1_genuine = float(f1_score(all_targets == 0, all_preds == 0, zero_division=0))

    prec_forged = prec
    rec_forged = rec
    f1_forged = f1

    return {
        "loss": round(epoch_loss, 4),
        "accuracy": round(acc * 100.0, 2),
        "precision": round(prec * 100.0, 2),
        "recall": round(rec * 100.0, 2),
        "f1": round(f1 * 100.0, 2),
        "genuine_precision": round(prec_genuine * 100.0, 2),
        "genuine_recall": round(rec_genuine * 100.0, 2),
        "genuine_f1": round(f1_genuine * 100.0, 2),
        "forged_precision": round(prec_forged * 100.0, 2),
        "forged_recall": round(rec_forged * 100.0, 2),
        "forged_f1": round(f1_forged * 100.0, 2),
        "total_samples": total,
    }


# =========================================================
# MAIN TRAINING PIPELINE
# =========================================================

def train(args):
    # 1. Device detection & logging
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        device_name = f"CUDA/GPU ({torch.cuda.get_device_name(0)})"
    else:
        device = torch.device("cpu")
        device_name = "CPU"
        torch.set_num_threads(os.cpu_count() or 4)

    print("\n=============================================================")
    print("DOCSHIELD AI: DOCUMENT FORGERY DETECTION ML PIPELINE")
    print("=============================================================")
    print(f"Selected Device:            {device_name}")
    print(f"Model Architecture:         {args.arch}")
    print(f"Epochs:                     {args.epochs}")
    print(f"Batch Size:                 {args.batch_size}")
    print(f"Learning Rate:              {args.lr}")
    print(f"Early Stopping Patience:    {args.patience}")
    print(f"Dataset Root:               {DATASET_ROOT}")
    print("=============================================================\n")

    # 2. Prepare Datasets & DataLoaders
    train_transform, eval_transform = get_data_transforms()

    train_dir = os.path.join(DATASET_ROOT, "train")
    val_dir = os.path.join(DATASET_ROOT, "validation")
    test_dir = os.path.join(DATASET_ROOT, "test")

    train_dataset = DocumentImageFolder(train_dir, transform=train_transform)
    val_dataset = DocumentImageFolder(val_dir, transform=eval_transform)
    test_dataset = DocumentImageFolder(test_dir, transform=eval_transform)

    # Require provenance for every image before fitting a model.
    from backend.intelligence.training import audit_image_folders
    provenance = audit_image_folders(DATASET_ROOT, {
        "train": train_dataset.samples,
        "validation": val_dataset.samples,
        "test": test_dataset.samples,
    })
    if not provenance["safe_to_train"]:
        raise ValueError("Training blocked by dataset provenance audit: " + str(provenance))

    # Calculate class weights to handle imbalance
    train_targets = [s[1] for s in train_dataset.samples]
    n_samples = len(train_targets)
    n_genuine = train_targets.count(0)
    n_forged = train_targets.count(1)

    w_genuine = n_samples / (2.0 * n_genuine)
    # Give a slight boost to forged weight to penalize missing forged documents
    w_forged = (n_samples / (2.0 * n_forged)) * 1.15
    class_weights_tensor = torch.tensor([w_genuine, w_forged], dtype=torch.float32).to(device)

    print(f"Class Imbalance Handling: Genuine Weight = {w_genuine:.3f}, Forged Weight = {w_forged:.3f}")
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

    # Optional subsampling for rapid training on CPU if requested
    if args.max_train_samples and args.max_train_samples < len(train_dataset):
        indices = np.random.choice(len(train_dataset), args.max_train_samples, replace=False)
        train_dataset = torch.utils.data.Subset(train_dataset, indices)
        print(f"Subsampled training set to {args.max_train_samples} samples as requested.")

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,  # Windows-friendly
        pin_memory=(device.type == "cuda")
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=(device.type == "cuda")
    )

    # 3. Model construction
    model = build_model(arch=args.arch, pretrained=True).to(device)

    # 4. Pre-training sanity check
    raw_train_ds = train_dataset.dataset if isinstance(train_dataset, torch.utils.data.Subset) else train_dataset
    run_sanity_check(raw_train_ds, val_dataset, model, criterion, device)

    if args.sanity_check_only:
        print("[*] Sanity check completed successfully. Exiting as --sanity-check-only was specified.")
        return

    # Reset model to ensure clean weights after sanity check step
    model = build_model(arch=args.arch, pretrained=True).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    # 5. Training loop with early stopping
    history = {
        "model_architecture": args.arch,
        "selected_device": device_name,
        "class_mapping": CLASS_TO_IDX,
        "image_size": list(IMAGE_SIZE),
        "class_weights": [round(w_genuine, 4), round(w_forged, 4)],
        "best_epoch": 0,
        "epochs": []
    }

    best_val_f1 = -1.0
    best_val_loss = float("inf")
    patience_counter = 0
    best_model_state = None
    best_metrics = {}

    start_training_time = time.time()

    for epoch in range(1, args.epochs + 1):
        epoch_start = time.time()
        model.train()
        running_train_loss = 0.0
        train_preds = []
        train_targets_list = []

        total_batches = len(train_loader)
        for batch_idx, (images, targets) in enumerate(train_loader, 1):
            images = images.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_train_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)

            train_preds.extend(preds.cpu().numpy())
            train_targets_list.extend(targets.cpu().numpy())

            if batch_idx % max(1, total_batches // 4) == 0 or batch_idx == total_batches:
                current_loss = running_train_loss / (batch_idx * args.batch_size)
                print(f"  Epoch [{epoch}/{args.epochs}] Batch [{batch_idx}/{total_batches}] - Loss: {current_loss:.4f}")

        scheduler.step()

        # Training metrics
        train_total = len(train_targets_list)
        epoch_train_loss = running_train_loss / max(1, train_total)
        train_acc = float(accuracy_score(train_targets_list, train_preds)) * 100.0
        train_prec = float(precision_score(train_targets_list, train_preds, zero_division=0)) * 100.0
        train_rec = float(recall_score(train_targets_list, train_preds, zero_division=0)) * 100.0
        train_f1 = float(f1_score(train_targets_list, train_preds, zero_division=0)) * 100.0

        # Validation metrics
        val_metrics = evaluate_loader(model, val_loader, criterion, device)
        epoch_time = time.time() - epoch_start

        epoch_record = {
            "epoch": epoch,
            "duration_seconds": round(epoch_time, 1),
            "train": {
                "loss": round(epoch_train_loss, 4),
                "accuracy": round(train_acc, 2),
                "precision": round(train_prec, 2),
                "recall": round(train_rec, 2),
                "f1": round(train_f1, 2),
            },
            "validation": val_metrics
        }
        history["epochs"].append(epoch_record)

        print(
            f"\n>>> Epoch {epoch:02d}/{args.epochs:02d} ({epoch_time:.1f}s) | "
            f"Train Loss: {epoch_train_loss:.4f} Acc: {train_acc:.2f}% F1: {train_f1:.2f}% | "
            f"Val Loss: {val_metrics['loss']:.4f} Acc: {val_metrics['accuracy']:.2f}% "
            f"Forged Rec: {val_metrics['forged_recall']:.2f}% Val F1: {val_metrics['f1']:.2f}%\n"
        )

        # Check for improvement (prioritize validation F1 and balanced performance)
        val_f1 = val_metrics["f1"]
        if val_f1 > best_val_f1 or (abs(val_f1 - best_val_f1) < 0.5 and val_metrics["loss"] < best_val_loss):
            best_val_f1 = val_f1
            best_val_loss = val_metrics["loss"]
            best_epoch = epoch
            best_model_state = {k: v.cpu() for k, v in model.state_dict().items()}
            best_metrics = val_metrics
            patience_counter = 0

            # Save best checkpoint
            checkpoint = {
                "model_state_dict": best_model_state,
                "class_to_idx": CLASS_TO_IDX,
                "idx_to_class": IDX_TO_CLASS,
                "arch": args.arch,
                "image_size": list(IMAGE_SIZE),
                "selected_device": device_name,
                "best_epoch": best_epoch,
                "val_metrics": best_metrics,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            torch.save(checkpoint, MODEL_SAVE_PATH)
            print(f"  [+] New best checkpoint saved to {MODEL_SAVE_PATH} (Epoch {best_epoch}, Val F1: {best_val_f1:.2f}%)")
        else:
            patience_counter += 1
            print(f"  [-] No improvement for {patience_counter} epoch(s). Best was Epoch {best_epoch} (Val F1: {best_val_f1:.2f}%)")
            if patience_counter >= args.patience:
                print(f"\n[EARLY STOPPING] Validation performance has ceased improving after {args.patience} epochs.")
                break

    total_training_duration = time.time() - start_training_time
    history["best_epoch"] = best_epoch
    history["total_duration_seconds"] = round(total_training_duration, 1)

    # Save training history JSON
    with open(TRAIN_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print("\n=============================================================")
    print(f"TRAINING COMPLETE in {total_training_duration:.1f}s")
    print(f"Best Checkpoint: Epoch {best_epoch} saved at {MODEL_SAVE_PATH}")
    print(f"Training History saved at {TRAIN_HISTORY_PATH}")
    print("=============================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Document Forgery ML Training")
    parser.add_argument("--arch", type=str, default="mobilenet_v3_small", choices=["mobilenet_v3_small", "resnet18"], help="Model architecture")
    parser.add_argument("--epochs", type=int, default=10, help="Maximum number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=0.0008, help="Initial learning rate")
    parser.add_argument("--patience", type=int, default=3, help="Early stopping patience")
    parser.add_argument("--max-train-samples", type=int, default=None, help="Optional sample cap for training")
    parser.add_argument("--sanity-check-only", action="store_true", help="Run sanity check and exit immediately")

    args = parser.parse_args()
    train(args)
