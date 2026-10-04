"""Check standalone fixtures; uses stdlib plus optional Pillow pixel checks.

Credential scanning is heuristic, not a guarantee that arbitrary secrets are absent.
No application code is imported and no network requests are made.
"""
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "demo_samples"
DISCLAIMER = "DEMO SAMPLE — NOT A REAL FINANCIAL DOCUMENT"
SAMPLES = ("guaranteed_return", "broker_impersonation", "educational_control")
EXPECTED = {"manifest.json", "metadata/tampering.json", "images/original_demo.png", "images/tampered_demo.png"}
EXPECTED.update(f"{folder}/{sample}.{extension}" for sample in SAMPLES for folder, extension in (("text", "txt"), ("metadata", "json"), ("images", "png")))
REQUIRED = {"sample_id": str, "title": str, "expected_risk": str, "expected_findings": list, "expected_ocr_fields": dict, "expected_scam_signals": list, "notes": list, "disclaimer": str, "expectation_type": str}
SECRET_PATTERNS = [
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b",
    rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
    rb"\bAIza[A-Za-z0-9_-]{30,}\b",
    rb"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",
    rb"(?i)(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|password)\s*[\"']?\s*[:=]\s*[\"']?[^\s\"',}]{6,}",
    rb"https?://[^\s/@]+:[^\s/@]+@",
]


def main():
    failures = []
    def check(ok, message):
        print(f"{'PASS' if ok else 'FAIL'} {message}")
        if not ok:
            failures.append(message)

    parsed = {}
    for relative in sorted(EXPECTED):
        check((ROOT / relative).is_file(), f"Exists: {relative}")
    if not ROOT.is_dir():
        print("FAIL demo_samples directory is missing")
        return 1
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            check(False, f"Unsafe file path: {relative}")
            continue
        limit = 5 * 1024 * 1024 if path.suffix == ".png" else 256 * 1024
        size_ok = 0 < path.stat().st_size <= limit
        check(size_ok, f"Reasonable size: {relative}")
        if not size_ok:
            continue
        raw = path.read_bytes()
        check(not any(re.search(pattern, raw) for pattern in SECRET_PATTERNS), f"No credential patterns: {relative}")
        if path.suffix in (".txt", ".json"):
            try:
                content = raw.decode("utf-8")
                check(DISCLAIMER in content, f"Demo disclaimer: {relative}")
                if path.suffix == ".json":
                    parsed[relative] = json.loads(content)
                    check(isinstance(parsed[relative], dict), f"JSON object: {relative}")
            except (UnicodeError, ValueError) as error:
                check(False, f"Invalid UTF-8/JSON: {relative} ({error})")
        elif path.suffix == ".png":
            valid = raw.startswith(b"\x89PNG\r\n\x1a\n") and len(raw) >= 24 and raw[12:16] == b"IHDR"
            check(valid, f"PNG header: {relative}")
            if valid:
                width, height = struct.unpack(">II", raw[16:24])
                check(0 < width <= 4096 and 0 < height <= 4096, f"Image dimensions: {relative}")
            check(DISCLAIMER.encode("utf-8") in raw, f"Embedded demo disclaimer: {relative}")
        else:
            check(False, f"Unexpected file format: {relative}")

    for relative, data in parsed.items():
        if not relative.startswith("metadata/") or not isinstance(data, dict):
            continue
        check(all(isinstance(data.get(key), kind) for key, kind in REQUIRED.items()), f"Required metadata fields: {relative}")
        check(data.get("expected_risk") in ("high", "medium", "low"), f"Risk label: {relative}")
        check(data.get("sample_id") == ("document_tampering" if relative.endswith("tampering.json") else Path(relative).stem), f"Sample identity: {relative}")
        check(data.get("disclaimer") == DISCLAIMER and "not production AI results" in str(data.get("expectation_type")), f"QA-only labeling: {relative}")
        check(all(isinstance(data.get(key), list) and all(isinstance(item, str) for item in data[key]) for key in ("expected_findings", "expected_scam_signals", "notes")), f"Metadata list values: {relative}")
    manifest = parsed.get("manifest.json", {})
    entries = manifest.get("assets", []) if isinstance(manifest, dict) else []
    entries_ok = isinstance(entries, list) and all(isinstance(entry, dict) and all(isinstance(entry.get(key), str) and entry[key] for key in ("path", "sample_id", "category", "purpose")) for entry in entries)
    check(entries_ok, "Manifest entry schema")
    if entries_ok:
        listed = [entry["path"] for entry in entries]
        check(len(listed) == len(set(listed)) and set(listed) == EXPECTED - {"manifest.json"}, "Manifest lists every expected payload exactly once")
        check(all(entry["category"] in ("scam_language", "impersonation", "normal_control", "document_tampering") for entry in entries), "Manifest categories")
    control = parsed.get("metadata/educational_control.json", {})
    check(isinstance(control, dict) and control.get("expected_risk") == "low" and control.get("expected_scam_signals") == [], "Educational sample is a low-risk control")

    try:
        from PIL import Image, ImageChops
    except ImportError:
        print("SKIP pixel integrity checks (Pillow unavailable); PNG headers and embedded disclaimers checked")
    else:
        try:
            for path in (ROOT / "images").glob("*.png"):
                with Image.open(path) as image:
                    image.verify()
            check(True, "PNG integrity")
            with Image.open(ROOT / "images/original_demo.png") as first, Image.open(ROOT / "images/tampered_demo.png") as second:
                check(first.size == second.size == (1800, 1100), "Tampering pair dimensions")
                bounds = ImageChops.difference(first.convert("RGB"), second.convert("RGB")).getbbox()
                metadata = parsed["metadata/tampering.json"]
                check(bounds is not None and list(bounds) == metadata["change"]["bounding_box_xyxy"], "Pixel differences match the declared tampering region exactly")
                check(metadata["change"]["before"] == "₹5,000" and metadata["change"]["after"] == "₹50,000", "Tampering before/after metadata")
        except Exception as error:
            check(False, f"Image/pair validation: {error}")
    print(f"\n{'FAIL' if failures else 'PASS'}: demo asset QA ({len(failures)} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
