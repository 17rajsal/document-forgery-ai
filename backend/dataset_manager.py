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
    random.seed(seed)

    # Group by (document_type, label, base_id) for stratified grouping
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        bid = r.get("base_id") or r.get("filename", "")
        base_prefix = bid.split("_var")[0].split("_aug")[0]
        group_key = f"{r['document_type']}_{r['label']}_{base_prefix}"
        groups.setdefault(group_key, []).append(r)

    # Stratify by (document_type, label)
    strata: Dict[str, List[str]] = {}
    for gkey, items in groups.items():
        doc_type = items[0]["document_type"]
        label = items[0]["label"]
        stratum_key = f"{doc_type}_{label}"
        strata.setdefault(stratum_key, []).append(gkey)

    train_records = []
    val_records = []
    test_records = []

    for stratum_key, gkeys in strata.items():
        random.shuffle(gkeys)
        n = len(gkeys)
        n_train = int(round(n * train_ratio))
        n_val = int(round(n * val_ratio))
        if n_train + n_val > n:
            n_train = max(1, n - n_val)

        train_keys = set(gkeys[:n_train])
        val_keys = set(gkeys[n_train:n_train + n_val])
        test_keys = set(gkeys[n_train + n_val:])

        # Ensure small categories have validation and test coverage
        if n >= 3:
            if not val_keys and len(train_keys) > 1:
                moved = list(train_keys)[-1]
                train_keys.remove(moved)
                val_keys.add(moved)
            if not test_keys and len(train_keys) > 1:
                moved = list(train_keys)[-1]
                train_keys.remove(moved)
                test_keys.add(moved)

        for gk in gkeys:
            items = groups[gk]
            if gk in train_keys:
                for it in items:
                    it["split"] = "train"
                    train_records.append(it)
            elif gk in val_keys:
                for it in items:
                    it["split"] = "validation"
                    val_records.append(it)
            else:
                for it in items:
                    it["split"] = "test"
                    test_records.append(it)

    return train_records, val_records, test_records


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
