import os
import io
import re
import csv
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import cv2

from dataset_manager import DATASET_DIR, MANIFEST_PATH, create_grouped_splits, save_manifest

DOCS_DIR = os.path.join(DATASET_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

CATEGORIES = [
    "id_card",
    "certificate",
    "marksheet",
    "invoice_receipt",
    "general_scanned",
]


def get_default_font(size=20, bold=False):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            continue
    return ImageFont.load_default()


def create_id_card(doc_id: str, tampered: bool = False, variation: str = "original") -> Image.Image:
    """Generates an ID card with photo placeholder, card details, barcode, and optional tampering."""
    w, h = 800, 500
    img = Image.new("RGB", (w, h), color=(248, 249, 252))
    draw = ImageDraw.Draw(img)

    # Header banner
    draw.rectangle([(0, 0), (w, 80)], fill=(30, 64, 175))
    draw.text((30, 24), "APEX TECHNICAL UNIVERSITY - STUDENT ID", fill=(255, 255, 255), font=get_default_font(24, True))

    # Photo box
    draw.rectangle([(40, 110), (200, 310)], fill=(220, 226, 240), outline=(150, 160, 180), width=2)
    draw.text((75, 195), "[ PHOTO ]", fill=(100, 116, 139), font=get_default_font(18, True))

    # Card fields
    name = f"VIKRAM ADITYA {doc_id[-3:]}"
    roll = f"TU-2024-88{doc_id[-3:]}"
    dob = "14/08/2002"
    blood = "B+ POSITIVE"
    valid = "2024 - 2028"

    font_label = get_default_font(18, True)
    font_val = get_default_font(18, False)

    fields = [
        ("FULL NAME:", name),
        ("ROLL NO:", roll),
        ("DATE OF BIRTH:", dob),
        ("BLOOD GROUP:", blood),
        ("VALID THRU:", valid),
    ]

    y = 115
    for lbl, val in fields:
        draw.text((230, y), lbl, fill=(30, 41, 59), font=font_label)
        if tampered and lbl == "ROLL NO:":
            # Spliced mismatched font height and color
            spliced_font = get_default_font(28, True)
            draw.text((400, y - 6), val + "99", fill=(10, 10, 10), font=spliced_font)
        else:
            draw.text((400, y), val, fill=(71, 85, 105), font=font_val)
        y += 42

    # Barcode representation
    for x_bar in range(40, 760, 6):
        bar_w = random.choice([2, 3, 4])
        draw.rectangle([(x_bar, 410), (x_bar + bar_w, 460)], fill=(20, 20, 20))

    if tampered:
        # Add copy-move duplicated stamp or spliced patch
        patch = img.crop((40, 110, 140, 210))
        img.paste(patch, (650, 120))

    return img


def create_certificate(doc_id: str, tampered: bool = False, variation: str = "original") -> Image.Image:
    """Generates an academic or achievement certificate."""
    w, h = 1000, 700
    img = Image.new("RGB", (w, h), color=(255, 253, 245))
    draw = ImageDraw.Draw(img)

    # Ornate double border
    draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(180, 140, 50), width=4)
    draw.rectangle([(35, 35), (w - 35, h - 35)], outline=(220, 180, 80), width=2)

    # Title
    draw.text((280, 80), "CERTIFICATE OF EXCELLENCE", fill=(120, 53, 15), font=get_default_font(32, True))
    draw.text((360, 140), "THIS IS PROUDLY PRESENTED TO", fill=(100, 116, 139), font=get_default_font(18, False))

    recipient = f"ANANYA SHARMA {doc_id[-3:]}"
    draw.text((310, 190), recipient, fill=(30, 41, 59), font=get_default_font(34, True))

    body = (
        "For outstanding academic performance and demonstration of advanced technical competence\n"
        "in the professional engineering curriculum during the academic year 2024-2025."
    )
    draw.text((120, 280), body, fill=(51, 65, 85), font=get_default_font(20, False))

    # Signatures
    draw.line([(150, 560), (380, 560)], fill=(100, 116, 139), width=2)
    draw.text((180, 575), "Director of Academics", fill=(71, 85, 105), font=get_default_font(18, False))

    draw.line([(620, 560), (850, 560)], fill=(100, 116, 139), width=2)
    draw.text((660, 575), "Chancellor / Registrar", fill=(71, 85, 105), font=get_default_font(18, False))

    # Stamp circle
    draw.ellipse([(440, 500), (560, 620)], outline=(180, 83, 9), width=3)
    draw.text((465, 550), "OFFICIAL\n  SEAL", fill=(180, 83, 9), font=get_default_font(16, True))

    if tampered:
        # Copy-move duplication: paste duplicate seal elsewhere
        seal_crop = img.crop((440, 500, 560, 620))
        img.paste(seal_crop, (820, 80))
        # Spliced grade text
        draw.text((300, 360), "GRADE: A++ FIRST CLASS", fill=(0, 0, 0), font=get_default_font(30, True))

    return img


def create_marksheet(doc_id: str, tampered: bool = False, variation: str = "original") -> Image.Image:
    """Generates an academic marksheet with tabular course grades."""
    w, h = 900, 800
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (w, 60)], fill=(15, 23, 42))
    draw.text((220, 16), "CENTRAL BOARD OF SECONDARY EDUCATION", fill=(255, 255, 255), font=get_default_font(22, True))
    draw.text((320, 80), "STATEMENT OF MARKS - CLASS XII", fill=(30, 41, 59), font=get_default_font(20, True))

    # Student metadata
    draw.text((60, 130), f"CANDIDATE NAME: RAHUL KUMAR {doc_id[-3:]}", fill=(51, 65, 85), font=get_default_font(16, True))
    draw.text((60, 160), f"ROLL NUMBER: 261739{doc_id[-3:]}", fill=(51, 65, 85), font=get_default_font(16, True))
    draw.text((550, 130), "SCHOOL: DELHI PUBLIC SCHOOL", fill=(51, 65, 85), font=get_default_font(16, False))
    draw.text((550, 160), "ACADEMIC YEAR: 2024", fill=(51, 65, 85), font=get_default_font(16, False))

    # Table Header
    draw.rectangle([(50, 210), (850, 250)], fill=(241, 245, 249), outline=(203, 213, 225), width=1)
    draw.text((70, 222), "CODE", fill=(15, 23, 42), font=get_default_font(16, True))
    draw.text((160, 222), "SUBJECT NAME", fill=(15, 23, 42), font=get_default_font(16, True))
    draw.text((470, 222), "MAX", fill=(15, 23, 42), font=get_default_font(16, True))
    draw.text((580, 222), "OBTAINED", fill=(15, 23, 42), font=get_default_font(16, True))
    draw.text((720, 222), "GRADE", fill=(15, 23, 42), font=get_default_font(16, True))

    subjects = [
        ("301", "ENGLISH CORE", "100", "88", "A2"),
        ("041", "MATHEMATICS", "100", "92", "A1"),
        ("042", "PHYSICS", "100", "85", "B1"),
        ("043", "CHEMISTRY", "100", "90", "A1"),
        ("083", "COMPUTER SCIENCE", "100", "96", "A1"),
    ]

    y = 260
    for code, sname, maxm, obt, grd in subjects:
        draw.line([(50, y + 35), (850, y + 35)], fill=(226, 232, 240), width=1)
        draw.text((70, y + 8), code, fill=(71, 85, 105), font=get_default_font(16, False))
        draw.text((160, y + 8), sname, fill=(51, 65, 85), font=get_default_font(16, False))
        draw.text((480, y + 8), maxm, fill=(71, 85, 105), font=get_default_font(16, False))

        if tampered and code == "042":
            # Tampered Physics score spliced with different font and baseline jump
            draw.text((580, y + 2), "99", fill=(0, 0, 0), font=get_default_font(26, True))
            draw.text((730, y + 2), "A1", fill=(0, 0, 0), font=get_default_font(26, True))
        else:
            draw.text((590, y + 8), obt, fill=(51, 65, 85), font=get_default_font(16, False))
            draw.text((730, y + 8), grd, fill=(51, 65, 85), font=get_default_font(16, False))
        y += 45

    draw.text((50, y + 50), "RESULT: PASS IN FIRST DIVISION", fill=(16, 185, 129), font=get_default_font(18, True))
    return img


def create_invoice(doc_id: str, tampered: bool = False, variation: str = "original") -> Image.Image:
    """Generates a business tax invoice or commercial receipt."""
    w, h = 850, 750
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.text((50, 40), "GLOBAL CLOUD TECHNOLOGIES PVT LTD", fill=(15, 23, 42), font=get_default_font(22, True))
    draw.text((50, 75), "GSTIN: 07AAAAA0000A1Z5 | PAN: AAAAA0000A", fill=(100, 116, 139), font=get_default_font(15, False))
    draw.text((50, 98), "Plot 42, Tech Park, Okhla Phase III, New Delhi 110020", fill=(100, 116, 139), font=get_default_font(14, False))

    draw.text((580, 40), "TAX INVOICE", fill=(30, 64, 175), font=get_default_font(26, True))
    draw.text((580, 80), f"Invoice #: INV-2025-{doc_id[-3:]}", fill=(51, 65, 85), font=get_default_font(16, True))
    draw.text((580, 105), "Date: 12-FEB-2025", fill=(71, 85, 105), font=get_default_font(15, False))

    draw.line([(50, 150), (800, 150)], fill=(203, 213, 225), width=2)
    draw.text((50, 165), "BILLED TO:", fill=(15, 23, 42), font=get_default_font(16, True))
    draw.text((50, 190), f"Enterprise Client Solutions LLC (Client #{doc_id[-3:]})", fill=(51, 65, 85), font=get_default_font(15, False))
    draw.text((50, 212), "128 Commerce Way, Sector 62, Noida UP", fill=(71, 85, 105), font=get_default_font(14, False))

    # Items table
    draw.rectangle([(50, 260), (800, 295)], fill=(248, 250, 252), outline=(226, 232, 240))
    draw.text((65, 270), "DESCRIPTION", fill=(30, 41, 59), font=get_default_font(15, True))
    draw.text((450, 270), "QTY", fill=(30, 41, 59), font=get_default_font(15, True))
    draw.text((540, 270), "UNIT PRICE", fill=(30, 41, 59), font=get_default_font(15, True))
    draw.text((680, 270), "TOTAL", fill=(30, 41, 59), font=get_default_font(15, True))

    items = [
        ("Cloud Infrastructure Hosting (AWS Enterprise Tier)", "1", "1,200.00", "1,200.00"),
        ("Database Redundancy & Automated Backup Svc", "2", "350.00", "700.00"),
        ("24x7 Security Operations Center Monitoring", "1", "850.00", "850.00"),
    ]

    y = 310
    for desc, qty, unit, tot in items:
        draw.text((65, y), desc, fill=(71, 85, 105), font=get_default_font(15, False))
        draw.text((460, y), qty, fill=(71, 85, 105), font=get_default_font(15, False))
        draw.text((550, y), f"${unit}", fill=(71, 85, 105), font=get_default_font(15, False))
        draw.text((690, y), f"${tot}", fill=(51, 65, 85), font=get_default_font(15, True))
        y += 40

    draw.line([(50, y + 10), (800, y + 10)], fill=(203, 213, 225), width=2)
    draw.text((520, y + 25), "SUBTOTAL:", fill=(71, 85, 105), font=get_default_font(16, True))
    draw.text((680, y + 25), "$2,750.00", fill=(71, 85, 105), font=get_default_font(16, True))

    draw.text((520, y + 55), "TAX (GST 18%):", fill=(71, 85, 105), font=get_default_font(16, True))
    draw.text((680, y + 55), "$495.00", fill=(71, 85, 105), font=get_default_font(16, True))

    draw.rectangle([(500, y + 90), (800, y + 135)], fill=(239, 246, 255), outline=(191, 219, 254))
    draw.text((520, y + 102), "GRAND TOTAL:", fill=(30, 64, 175), font=get_default_font(18, True))

    if tampered:
        # Spliced grand total with different font
        draw.text((670, y + 96), "$9,999.00", fill=(185, 28, 28), font=get_default_font(26, True))
        # Add duplicate stamp for copy-move tampering
        draw.rectangle([(50, y + 80), (180, y + 130)], outline=(185, 28, 28), width=3)
        draw.text((70, y + 95), "PAID STAMP", fill=(185, 28, 28), font=get_default_font(16, True))
        stamp_crop = img.crop((50, y + 80, 180, y + 130))
        img.paste(stamp_crop, (280, y + 80))
    else:
        draw.text((680, y + 102), "$3,245.00", fill=(30, 64, 175), font=get_default_font(18, True))

    return img


def create_general_scanned(doc_id: str, tampered: bool = False, variation: str = "original") -> Image.Image:
    """Generates a formal contractual or governmental scanned letter."""
    w, h = 850, 850
    img = Image.new("RGB", (w, h), color=(250, 250, 248))
    draw = ImageDraw.Draw(img)

    draw.text((300, 50), "OFFICIAL DIRECTIVE & AGREEMENT", fill=(15, 23, 42), font=get_default_font(20, True))
    draw.text((340, 85), "MINISTRY OF COMMERCE & INDUSTRY", fill=(71, 85, 105), font=get_default_font(16, False))
    draw.line([(80, 120), (770, 120)], fill=(148, 163, 184), width=1)

    draw.text((80, 145), f"Ref No: MCI/REG/2025/{doc_id[-3:]}", fill=(51, 65, 85), font=get_default_font(15, True))
    draw.text((600, 145), "Date: 15 January 2025", fill=(71, 85, 105), font=get_default_font(15, False))

    paragraphs = [
        "1. In accordance with Section 14 of the National Trade Authorization Act, this directive confirms",
        "the verified registration status of the authorized entity identified in Schedule A below.",
        "",
        "2. The verified entity is granted non-exclusive rights to conduct electronic data processing",
        "and document verification operations within accredited sovereign jurisdictional boundaries.",
        "",
        "3. Any unauthorized reproduction, modification of text, or deletion of security seals constitutes",
        "a severe statutory offense under the Digital Authentication Act of 2000.",
    ]

    y = 200
    for p in paragraphs:
        if p:
            draw.text((80, y), p, fill=(30, 41, 59), font=get_default_font(16, False))
        y += 32

    # Schedule box
    draw.rectangle([(80, y + 20), (770, y + 160)], fill=(241, 245, 249), outline=(203, 213, 225))
    draw.text((100, y + 35), f"SCHEDULE A: Entity Registration ID #{doc_id[-3:]}992", fill=(15, 23, 42), font=get_default_font(16, True))
    draw.text((100, y + 70), "Status: FULLY COMPLIANT AND RATIFIED", fill=(22, 101, 52), font=get_default_font(16, True))
    draw.text((100, y + 105), "Valid Until: 31-DEC-2028", fill=(71, 85, 105), font=get_default_font(15, False))

    if tampered:
        # Splice tampered text into Schedule A
        draw.rectangle([(280, y + 68), (550, y + 96)], fill=(241, 245, 249))
        draw.text((280, y + 65), "REVOKED / CANCELLED", fill=(220, 38, 38), font=get_default_font(24, True))
        # Add duplicate seal for copy-move tampering
        draw.ellipse([(620, y + 25), (740, y + 145)], outline=(180, 20, 20), width=3)
        draw.text((645, y + 70), "SEAL / DRAFT", fill=(180, 20, 20), font=get_default_font(14, True))
        seal_crop = img.crop((620, y + 25, 740, y + 145))
        img.paste(seal_crop, (80, y + 25))

    return img


def apply_variation(img: Image.Image, variation: str) -> Image.Image:
    """Applies realistic scanning, re-compression, or screenshot effects."""
    if variation == "scan":
        # Scanner effect: subtle rotation, noise, slight blur
        rotated = img.rotate(random.uniform(-0.8, 0.8), resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))
        # Add scanner grain
        np_img = np.array(rotated, dtype=np.float32)
        noise = np.random.normal(0, 3.5, np_img.shape)
        noisy = np.clip(np_img + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy)

    elif variation == "compressed":
        # Multi-generation JPEG recompression
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=random.randint(35, 45))
        buf.seek(0)
        recomp = Image.open(buf)
        buf2 = io.BytesIO()
        recomp.save(buf2, format="JPEG", quality=55)
        buf2.seek(0)
        return Image.open(buf2).convert("RGB")

    elif variation == "screenshot":
        # Digital screenshot appearance (clean, crisp, PNG format)
        return img.copy()

    return img


def inject_editing_metadata(file_path: str):
    """Appends editing tool binary markers for realistic software forensics."""
    tags = [
        b"\n<!-- Adobe Photoshop 2024 (Windows) XMP Core 7.1 -->\n",
        b"\n<!-- GIMP 2.10.34 (GNU Image Manipulation Program) -->\n",
        b"\n<!-- Created with Canva Design Suite -->\n",
    ]
    try:
        with open(file_path, "ab") as f:
            f.write(random.choice(tags))
    except Exception:
        pass


def generate_full_dataset(num_docs_per_category: int = 24):
    """
    Generates a balanced dataset of 120 base documents with realistic variations:
    - 5 Categories: id_card, certificate, marksheet, invoice_receipt, general_scanned
    - Labels: genuine, forged
    - Variations: original, scan, compressed, screenshot
    Creates manifest.csv with 60% train, 20% validation, 20% test splits.
    """
    records = []
    generators = {
        "id_card": create_id_card,
        "certificate": create_certificate,
        "marksheet": create_marksheet,
        "invoice_receipt": create_invoice,
        "general_scanned": create_general_scanned,
    }

    print(f"Generating synthetic dataset across {len(CATEGORIES)} categories...")

    for cat in CATEGORIES:
        gen_func = generators[cat]
        for i in range(1, num_docs_per_category + 1):
            doc_id = f"{cat}_{i:03d}"

            # 1. Genuine Base Document
            img_genuine = gen_func(doc_id, tampered=False)
            g_variations = [
                ("orig", "original"),
                ("scan", "scan"),
                ("comp", "compressed"),
                ("shot", "screenshot"),
            ]
            for var_code, var_name in g_variations:
                v_img = apply_variation(img_genuine, var_name)
                ext = ".png" if var_name == "screenshot" else ".jpg"
                fname = f"{doc_id}_{var_code}{ext}"
                out_path = os.path.join(DOCS_DIR, fname)

                if ext == ".png":
                    v_img.save(out_path, format="PNG")
                else:
                    v_img.save(out_path, format="JPEG", quality=85 if var_name != "compressed" else 42)

                records.append({
                    "filename": fname,
                    "document_type": cat,
                    "label": "genuine",
                    "base_id": doc_id,
                })

            # 2. Forged Document
            img_forged = gen_func(doc_id, tampered=True)
            f_variations = [
                ("orig", "original"),
                ("scan", "scan"),
                ("comp", "compressed"),
            ]
            for var_code, var_name in f_variations:
                v_img = apply_variation(img_forged, var_name)
                fname = f"{doc_id}_forged_{var_code}.jpg"
                out_path = os.path.join(DOCS_DIR, fname)
                v_img.save(out_path, format="JPEG", quality=85)

                # Inject editing tool metadata (Photoshop / GIMP / Canva)
                inject_editing_metadata(out_path)

                records.append({
                    "filename": fname,
                    "document_type": cat,
                    "label": "forged",
                    "base_id": doc_id,
                })

    # Grouped split: 60% train, 20% validation, 20% test
    train_r, val_r, test_r = create_grouped_splits(records, train_ratio=0.60, val_ratio=0.20, test_ratio=0.20)
    all_split_records = train_r + val_r + test_r

    save_manifest(all_split_records, MANIFEST_PATH)
    print(f"Manifest written to {MANIFEST_PATH}: Total={len(all_split_records)} (Train={len(train_r)}, Val={len(val_r)}, Test={len(test_r)})")
    return all_split_records


if __name__ == "__main__":
    generate_full_dataset(num_docs_per_category=20)
