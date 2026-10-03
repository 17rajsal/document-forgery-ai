import os
import csv
import json
import random
from typing import Dict, List, Tuple, Any

DATASET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset"))
MANIFEST_PATH = os.path.join(DATASET_DIR, "manifest.csv")
SPLITS_PATH = os.path.join(DATASET_DIR, "splits.json")

DOCUMENT_CATEGORIES = [
    "id_card",
    "certificate",
    "marksheet",
    "invoice_receipt",
    "general_scanned",
]


def load_manifest(manifest_path: str = MANIFEST_PATH) -> List[Dict[str, Any]]:
    """
    Loads dataset manifest CSV.
    Expected headers: filename, document_type, label, [split, base_id]
    """
    if not os.path.exists(manifest_path):
        return []

    records = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "filename": row.get("filename", "").strip(),
                "document_type": row.get("document_type", "general_scanned").strip(),
                "label": row.get("label", "genuine").strip().lower(),
                "split": row.get("split", "").strip().lower(),
                "base_id": row.get("base_id", row.get("filename", "")).strip(),
            })
    return records


def create_grouped_splits(
    records: List[Dict[str, Any]],
    train_ratio: float = 0.60,
    val_ratio: float = 0.20,
    test_ratio: float = 0.20,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Partitions records into train, validation, and test splits using document-level
    grouping (base_id) so that all augmentations/crops/re-compressions of a document
    reside in the SAME split, preventing data leakage.
    """
    if min(train_ratio, val_ratio, test_ratio) < 0 or abs(train_ratio + val_ratio + test_ratio - 1) > 1e-8:
        raise ValueError("Split ratios must be nonnegative and sum to one")
    groups = {}
    for record in records:
        source = record.get("source_id") or record.get("base_id")
        if not source:
            raise ValueError("Explicit source identity is required for leakage-free splits")
        groups.setdefault(source, []).append(record)
    keys = sorted(groups)
    random.Random(seed).shuffle(keys)
    n_train = int(len(keys) * train_ratio)
    n_val = int(len(keys) * val_ratio)
    partitions = ([], [], [])
    for index, source in enumerate(keys):
        partition = 0 if index < n_train else 1 if index < n_train + n_val else 2
        split = ("train", "validation", "test")[partition]
        for record in groups[source]:
            partitions[partition].append({**record, "split": split})
    return partitions


def save_manifest(records: List[Dict[str, Any]], manifest_path: str = MANIFEST_PATH):
    """
    Saves manifest to CSV.
    """
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    fieldnames = ["filename", "document_type", "label", "split", "base_id"]
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({
                "filename": r.get("filename", ""),
                "document_type": r.get("document_type", ""),
                "label": r.get("label", ""),
                "split": r.get("split", ""),
                "base_id": r.get("base_id", r.get("filename", "")),
            })


def resolve_image_path(filename: str, split: str = "", label: str = "") -> str:
    """
    Resolves the absolute path for an image in the dataset or uploads folder.
    """
    if os.path.isabs(filename) and os.path.exists(filename):
        return filename

    if split and label:
        p = os.path.join(DATASET_DIR, split, label, filename)
        if os.path.exists(p):
            return p

    for s in ["train", "validation", "test", "docs", ""]:
        for l in ["genuine", "forged", ""]:
            p = os.path.join(DATASET_DIR, s, l, filename)
            if os.path.exists(p):
                return p

    backend_uploads = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads", filename))
    if os.path.exists(backend_uploads):
        return backend_uploads

    return os.path.join(DATASET_DIR, filename)
