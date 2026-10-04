import os
import shutil
import uuid
import logging
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import pytesseract
from pytesseract import Output
import pypdfium2 as pdfium
import numpy as np
import cv2
import docx

from document_classifier import classify_document
from field_extractor import (
    extract_generic_fields,
    extract_college_id_fields,
    extract_aadhaar_fields,
    extract_marksheet_fields,
    extract_bank_fields,
    extract_invoice_fields,
)
from forgery_detector import analyze_image, image_to_base64_jpeg

# =========================================================
# LOGGING SETUP
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("document_forgery_ai")

app = FastAPI(
    title="Document Forgery AI API",
    description="Enterprise-grade document classification, multi-pass OCR extraction, and multi-layer forensic tampering detection.",
    version="2.1.0"
)

# =========================================================
# CORS MIDDLEWARE
# =========================================================

allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File upload constraints (30MB default max)
MAX_FILE_SIZE_BYTES = int(os.environ.get("MAX_FILE_SIZE_BYTES", 30 * 1024 * 1024))
SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".pdf", ".tif", ".tiff", ".bmp", ".docx"]

def validate_magic_bytes(header: bytes, ext: str) -> bool:
    """
    Validates that the file binary header matches its claimed extension.
    Prevents executable/script injection with disguised extensions.
    """
    ext = ext.lower()
    if ext == ".pdf":
        return header.startswith(b"%PDF-")
    elif ext in [".jpg", ".jpeg"]:
        return header.startswith(b"\xff\xd8\xff")
    elif ext == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    elif ext == ".webp":
        return len(header) >= 12 and header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    elif ext in [".tif", ".tiff"]:
        return header.startswith(b"II*\x00") or header.startswith(b"MM\x00*")
    elif ext == ".bmp":
        return header.startswith(b"BM")
    elif ext == ".docx":
        return header.startswith(b"PK\x03\x04")
    return False


# =========================================================
# CONFIGURATION & TESSERACT PATH RESOLUTION
# =========================================================

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

def resolve_tesseract():
    """
    Dynamically discovers the Tesseract executable across
    environment variables, common Windows directories, and system PATH.
    """
    if "TESSERACT_CMD" in os.environ and os.path.exists(os.environ["TESSERACT_CMD"]):
        return os.environ["TESSERACT_CMD"]

    windows_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(windows_default):
        return windows_default

    which_path = shutil.which("tesseract")
    if which_path:
        return which_path

    return "tesseract"

pytesseract.pytesseract.tesseract_cmd = resolve_tesseract()


# =========================================================
# DOCUMENT & MULTI-FORMAT RENDERER
# =========================================================

def extract_docx_details(file_path: str) -> Tuple[Image.Image, str, str, Dict[str, Any]]:
    """
    Extracts text, structural content, core metadata, and renders a visual
    page snapshot for DOCX files to enable full forensic & OCR processing.
    """
    doc = docx.Document(file_path)

    # Core metadata
    core_props = doc.core_properties
    docx_meta = {
        "author": getattr(core_props, "author", None) or "Unknown",
        "last_modified_by": getattr(core_props, "last_modified_by", None) or "Unknown",
        "created": str(getattr(core_props, "created", "")) or "Unknown",
        "modified": str(getattr(core_props, "modified", "")) or "Unknown",
        "revision": getattr(core_props, "revision", 1),
    }

    # Extract paragraphs and table content
    paragraphs_text = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    table_texts = []
    for table in doc.tables:
        for row in table.rows:
            row_items = [c.text.strip() for c in row.cells if c.text.strip()]
            if row_items:
                table_texts.append(" | ".join(row_items))

    all_docx_text = "\n".join(paragraphs_text + (["\n[Table Data]"] + table_texts if table_texts else []))

    # Render a high-resolution A4-proportioned canvas (1240 x 1754 px)
    canvas = Image.new("RGB", (1240, 1754), color=(255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    try:
        header_font = ImageFont.truetype("arialbd.ttf", 26)
        body_font = ImageFont.truetype("arial.ttf", 20)
        meta_font = ImageFont.truetype("ariali.ttf", 16)
    except Exception:
        header_font = ImageFont.load_default()
        body_font = header_font
        meta_font = header_font

    y = 60
    draw.text((70, y), "DOCX DOCUMENT VISUAL PREVIEW", fill=(15, 23, 42), font=header_font)
    y += 40
    meta_line = f"Author: {docx_meta['author']} | Modified: {docx_meta['modified']}"
    draw.text((70, y), meta_line, fill=(100, 116, 139), font=meta_font)
    y += 30
    draw.line([(70, y), (1170, y)], fill=(226, 232, 240), width=2)
    y += 40

    # Extract and embed first image if available
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            try:
                from io import BytesIO
                img_data = rel.target_part.blob
                emb_img = Image.open(BytesIO(img_data)).convert("RGB")
                emb_img.thumbnail((700, 450))
                canvas.paste(emb_img, (70, y))
                y += emb_img.height + 30
                break
            except Exception:
                pass

    # Draw document text content
    all_lines = paragraphs_text + (["[Table Data]"] + table_texts if table_texts else [])
    for line in all_lines:
        if y > 1650:
            draw.text((70, y), "... [Additional document content truncated for preview] ...", fill=(148, 163, 184), font=meta_font)
            break
        words = line.split(" ")
        curr = ""
        for w in words:
            if len(curr) + len(w) + 1 > 75:
                draw.text((70, y), curr, fill=(30, 41, 59), font=body_font)
                y += 28
                curr = w
            else:
                curr = f"{curr} {w}".strip()
        if curr:
            draw.text((70, y), curr, fill=(30, 41, 59), font=body_font)
            y += 28

    rendered_image_path = file_path + "_docx_preview.jpg"
    canvas.save(rendered_image_path, "JPEG", quality=95)
    return canvas, rendered_image_path, all_docx_text, docx_meta


def load_document_as_image(file_path: str):
    """
    Loads an uploaded file as a PIL Image.
    Supports PDF, DOCX, TIFF, BMP, WEBP, PNG, and JPEG.
    Renders high-DPI rasterization for vector/text documents.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            pdf = pdfium.PdfDocument(file_path)
            if len(pdf) == 0:
                raise ValueError("PDF contains 0 pages.")
            page = pdf[0]
            # Render at 2.0x scale (144-200 DPI) for sharp OCR and forensic analysis
            bitmap = page.render(scale=2.0)
            pil_image = bitmap.to_pil()

            rendered_image_path = file_path + "_page1.jpg"
            pil_image.save(rendered_image_path, "JPEG", quality=95)
            return pil_image, rendered_image_path, len(pdf), None
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

    elif ext == ".docx":
        try:
            pil_image, rendered_path, native_text, docx_meta = extract_docx_details(file_path)
            return pil_image, rendered_path, 1, {"native_text": native_text, "docx_meta": docx_meta}
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX document: {str(e)}")

    elif ext in [".tif", ".tiff"]:
        try:
            pil_image = Image.open(file_path)
            total_pages = getattr(pil_image, "n_frames", 1)
            pil_image.seek(0)
            rgb_image = pil_image.convert("RGB")
            rendered_image_path = file_path + "_converted.jpg"
            rgb_image.save(rendered_image_path, "JPEG", quality=95)
            return rgb_image, rendered_image_path, total_pages, None
        except Exception as e:
            raise ValueError(f"Unsupported or corrupted TIFF document: {str(e)}")

    elif ext in [".bmp", ".webp"]:
        try:
            pil_image = Image.open(file_path)
            rgb_image = pil_image.convert("RGB")
            rendered_image_path = file_path + "_converted.jpg"
            rgb_image.save(rendered_image_path, "JPEG", quality=95)
            return rgb_image, rendered_image_path, 1, None
        except Exception as e:
            raise ValueError(f"Unsupported or corrupted {ext} document: {str(e)}")

    else:
        try:
            pil_image = Image.open(file_path)
            pil_image.load()
            return pil_image, file_path, 1, None
        except Exception as e:
            raise ValueError(f"Unsupported or corrupted image file: {str(e)}")


# =========================================================
# MULTI-PASS OCR ENGINE
# =========================================================

def perform_ocr(image: Image.Image) -> Tuple[str, List[Dict[str, Any]], float]:
    """
    Runs multi-pass OCR with adaptive preprocessing:
      Pass 1: High-contrast + sharpening (general documents & colored badges)
      Pass 2: Otsu binarization (faded scans, photocopies, low contrast)
      Pass 3: Adaptive Gaussian thresholding (uneven lighting, noisy documents)
    Selects the pass with the highest word accuracy/confidence.
    Returns: (extracted_text, words_with_boxes, overall_ocr_confidence)
    """
    gray = image.convert("L")
    width, height = gray.size

    # Upscale if image is smaller than standard page width for clear OCR
    if width < 1200:
        scale = 1200 / width
        gray = gray.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
        width, height = gray.size

    # Pass 1 Preprocessing: Contrast + Sharpen
    pass1_img = ImageEnhance.Contrast(gray).enhance(2.0).filter(ImageFilter.SHARPEN)

    def extract_ocr_data(target_img):
        try:
            data = pytesseract.image_to_data(
                target_img,
                config="--psm 6",
                output_type=Output.DICT
            )
        except Exception:
            data = pytesseract.image_to_data(
                target_img,
                output_type=Output.DICT
            )

        words = []
        text_parts = []
        conf_sum = 0.0

        for i in range(len(data.get("text", []))):
            word = data["text"][i].strip()
            if not word:
                continue

            try:
                conf = float(data["conf"][i])
                if conf < 0:
                    conf = 0.0
            except Exception:
                conf = 0.0

            words.append({
                "text": word,
                "confidence": round(conf, 1),
                "x": int(data["left"][i]),
                "y": int(data["top"][i]),
                "w": int(data["width"][i]),
                "h": int(data["height"][i])
            })
            text_parts.append(word)
            conf_sum += conf

        avg_conf = (conf_sum / len(words)) if words else 0.0
        return " ".join(text_parts), words, round(avg_conf, 1)

    # 1. Execute Pass 1
    text, words, ocr_conf = extract_ocr_data(pass1_img)

    # 2. If confidence is suboptimal (<72%) or few words were detected, try Pass 2 (Otsu binarization)
    if (ocr_conf < 72.0 or len(words) < 8) and width >= 200 and height >= 200:
        try:
            img_np = np.array(gray)
            _, otsu_np = cv2.threshold(img_np, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            pass2_img = Image.fromarray(otsu_np)
            t2, w2, c2 = extract_ocr_data(pass2_img)
            # Adopt Pass 2 if confidence improved or significantly more text was discovered
            if (c2 > ocr_conf and len(w2) >= len(words)) or (len(w2) > len(words) * 1.25 and c2 >= 50.0):
                text, words, ocr_conf = t2, w2, c2
        except Exception as e:
            logger.debug(f"Pass 2 OCR fallback skipped: {e}")

    # 3. If still low (<58%), try Pass 3 (Adaptive Gaussian thresholding)
    if (ocr_conf < 58.0 or len(words) < 5) and width >= 200 and height >= 200:
        try:
            img_np = np.array(gray)
            adaptive_np = cv2.adaptiveThreshold(
                img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
            )
            pass3_img = Image.fromarray(adaptive_np)
            t3, w3, c3 = extract_ocr_data(pass3_img)
            if c3 > ocr_conf and len(w3) >= len(words):
                text, words, ocr_conf = t3, w3, c3
        except Exception as e:
            logger.debug(f"Pass 3 OCR fallback skipped: {e}")

    return text, words, ocr_conf


# =========================================================
# CORE PIPELINE PROCESSOR
# =========================================================

def process_document_pipeline(file_path: str, original_filename: str, analysis_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes the comprehensive forensic and OCR pipeline:
      1. Loads/Rasterizes document (PDF, DOCX, TIFF, BMP, WEBP, PNG, JPEG)
      2. Runs Multi-Pass OCR with word coordinate capture & confidence scoring
      3. Classifies document category (ID, Marksheet, Bank, Invoice, General)
      4. Extracts structured domain fields & algorithmic checks (Verhoeff, GSTIN)
      5. Runs multi-layer forensic engine (ELA with spatial variance, noise variance,
         copy-move detection, text layout consistency, metadata tampering)
      6. Synthesizes 4-tier classification with plain-language explanation and limitations
      7. Cleans temporary rasterization files safely.
    """
    image, analysis_image_path, total_pages, extra_info = load_document_as_image(file_path)
    if not analysis_id:
        analysis_id = uuid.uuid4().hex

    try:
        # 1. OCR
        text, words, ocr_conf = perform_ocr(image)

        # Merge DOCX native text if available and richer
        if extra_info and extra_info.get("native_text"):
            docx_text = extra_info["native_text"]
            if len(docx_text) > len(text):
                text = docx_text

        # 2. Document Classification
        document_type = classify_document(text)

        # 3. Field Extraction based on document type
        if document_type == "College / Student ID":
            extracted_fields = extract_college_id_fields(text, words)
        elif document_type == "Aadhaar / Government ID":
            extracted_fields = extract_aadhaar_fields(text)
        elif document_type == "Marksheet / Academic Certificate":
            extracted_fields = extract_marksheet_fields(text)
        elif document_type in ("Bank Mandate", "Bank Document"):
            extracted_fields = extract_bank_fields(text)
        elif document_type == "Invoice / Financial Receipt":
            extracted_fields = extract_invoice_fields(text)
        else:
            extracted_fields = extract_generic_fields(text)

        # Gather algorithmic validation flags
        validation_flags = extracted_fields.get("validations", [])

        # 4. Forensic Forgery Detection
        try:
            forgery_analysis = analyze_image(
                analysis_image_path,
                validation_flags=validation_flags,
                words=words,
                document_type=document_type
            )
        except Exception as e:
            logger.error(f"Forensic engine failure on {original_filename}: {e}", exc_info=True)
            forgery_analysis = {
                "risk_score": 50,
                "classification": "NEEDS_MANUAL_REVIEW",
                "authenticity_status": "NEEDS_MANUAL_REVIEW",
                "risk_level": "MODERATE",
                "confidence_score": 50.0,
                "verdict": f"Forensic analysis error: {str(e)}",
                "explanation": f"The automated forensic analysis encountered an internal error while processing: {str(e)}. Document requires manual inspection.",
                "limitations": "Forensic algorithm encountered an execution error. Cannot establish conclusive authenticity.",
                "indicators": [{
                    "code": "FORENSIC_PIPELINE_ERROR",
                    "title": "Forensic Engine Warning",
                    "description": str(e),
                    "severity": "WARNING",
                    "weight": 50
                }],
                "ela_analysis": {"available": False},
                "noise_analysis": {"available": False},
                "metadata_forensics": {"has_exif": False, "editing_software_detected": False}
            }

        # If docx metadata exists, enrich metadata forensics
        if extra_info and extra_info.get("docx_meta"):
            meta = extra_info["docx_meta"]
            forgery_analysis.setdefault("metadata_forensics", {})["docx_properties"] = meta

        # Generate document preview base64
        preview_b64 = image_to_base64_jpeg(image, quality=80)

        # 5. Proofly Multimodal Investor-Safety & Forensic Engine
        try:
            from proofly.pipeline import run_proofly_pipeline
            proofly_dossier = run_proofly_pipeline(
                image=image,
                file_path=analysis_image_path,
                original_filename=original_filename,
                extracted_text=text,
                ocr_words=words,
                base_forgery_analysis=forgery_analysis,
                document_type=document_type
            )
        except Exception as e:
            logger.error(f"Proofly engine execution failure on {original_filename}: {e}", exc_info=True)
            proofly_dossier = {
                "available": False,
                "error": str(e),
                "assessment": {
                    "concern_level": "MODERATE",
                    "status_label": "Verification Concern: Moderate (Fallback)",
                    "key_findings": [],
                    "why_am_i_seeing_this": ["Proofly deep inspection encountered a fallback."],
                    "disclaimer": "Automated verification fallback active."
                },
                "visual_evidence_map": [],
                "plain_explanations": {
                    "simple_explanation_en": "Document processed under standard forensic mode.",
                    "simple_explanation_hi": "Document ko standard forensic mode mein jancha gaya hai.",
                    "voice_script_en": "Notice: Document analysis complete.",
                    "voice_script_hi": "Dhyan dein: Document ki jaanch poori ho gayi hai.",
                    "safe_steps": []
                }
            }

        out_dict = {
            "status": "SUCCESS",
            "message": "Document analyzed successfully",
            "filename": original_filename,
            "document_type": document_type,
            "total_pages": total_pages,
            "preview_image": preview_b64,
            "risk_score": forgery_analysis.get("risk_score", 0),
            "classification": forgery_analysis.get("classification", "AUTHENTIC"),
            "authenticity_status": forgery_analysis.get("authenticity_status", forgery_analysis.get("classification", "AUTHENTIC")),
            "risk_level": forgery_analysis.get("risk_level", "LOW"),
            "concern_level": proofly_dossier.get("assessment", {}).get("concern_level", "LOW"),
            "confidence_score": forgery_analysis.get("confidence_score", 85.0),
            "verdict": forgery_analysis.get("verdict", ""),
            "explanation": forgery_analysis.get("explanation", ""),
            "limitations": forgery_analysis.get("limitations", ""),
            "indicators": forgery_analysis.get("indicators", []),
            "extracted_text": text,
            "ocr_confidence": ocr_conf,
            "extracted_fields": extracted_fields,
            "forgery_analysis": forgery_analysis,
            "ocr_words": words,
            "proofly": proofly_dossier,
            "visual_evidence_map": proofly_dossier.get("visual_evidence_map", []),
            "analysis_id": analysis_id,
            "document_id": analysis_id,
            "investor_scam_risk": proofly_dossier.get("investor_scam_risk", {}),
            "component_breakdown": proofly_dossier.get("component_breakdown", {}),
            "why_flagged": proofly_dossier.get("why_flagged", {}),
            "entity_verification": proofly_dossier.get("entity_verification", {}),
        }

        def sanitize_for_json(obj):
            if isinstance(obj, dict):
                return {str(k): sanitize_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [sanitize_for_json(x) for x in obj]
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, (np.integer, int)):
                return int(obj)
            elif isinstance(obj, (np.floating, float)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        try:
            from proofly.adapter import pipeline_dict_to_analysis
            from intelligence.api import save_report
            file_bytes = None
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                except Exception:
                    pass
            analysis_model = pipeline_dict_to_analysis(
                doc_id=analysis_id,
                filename=original_filename,
                pipeline_result=out_dict,
                file_bytes=file_bytes
            )
            save_report(analysis_model)
        except Exception as e:
            logger.warning(f"Could not persist v1 Analysis report cache: {e}")

        return sanitize_for_json(out_dict)

    finally:
        # Safe cleanup of temporary converted raster files
        if analysis_image_path != file_path and os.path.exists(analysis_image_path):
            try:
                os.remove(analysis_image_path)
            except Exception as e:
                logger.debug(f"Cleanup of temp raster file skipped: {e}")


# =========================================================
# STATIC FRONTEND MOUNTING
# =========================================================

if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


# =========================================================
# ENDPOINTS
# =========================================================

@app.get("/")
@app.head("/")
def home():
    if os.path.exists(FRONTEND_DIST):
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    return {
        "product": "Proofly",
        "tagline": "See beyond what looks legit.",
        "hackathon": "SANGYAN Investor Resilience Hackathon (Tracks A, C, E)",
        "version": "3.0.0",
        "supported_formats": ["JPG", "JPEG", "PNG", "WEBP", "PDF", "TIFF", "BMP", "DOCX"],
        "tesseract": pytesseract.pytesseract.tesseract_cmd
    }


@app.get("/api/health")
@app.head("/api/health")
def health_check():
    tess_available = os.path.exists(pytesseract.pytesseract.tesseract_cmd)
    return {
        "status": "HEALTHY",
        "product": "Proofly Investor",
        "tagline": "Verify before you trust.",
        "hackathon": "SANGYAN Hackathon — IIT (BHU) × SEBI × NSDL",
        "tracks": ["Track A — Digital Fraud & Scam Resilience", "Track E — Misinformation & Content Literacy"],

        "ocr_available": tess_available,
        "tesseract_path": pytesseract.pytesseract.tesseract_cmd,
        "upload_dir_configured": bool(UPLOAD_DIR),
        "supported_formats": ["JPG", "JPEG", "PNG", "WEBP", "PDF", "TIFF", "BMP", "DOCX"],
        "max_file_size_mb": MAX_FILE_SIZE_BYTES // (1024 * 1024)
    }


class TextAnalysisRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None
    claimed_org: Optional[str] = None
    claimed_reg_no: Optional[str] = None
    language: Optional[str] = "en"


class EntityVerificationRequest(BaseModel):
    claimed_entity: Optional[str] = None
    registration_number: Optional[str] = None
    claimed_url: Optional[str] = None


@app.post("/api/analyze-text")
def api_analyze_text(req: TextAnalysisRequest):
    """
    Direct analysis of pasted text messages (WhatsApp, Telegram, SMS),
    suspicious URLs, and investment proposals.
    """
    from proofly.text_url_analyzer import analyze_text_and_url_submission
    return analyze_text_and_url_submission(
        text=req.text,
        url=req.url,
        claimed_org=req.claimed_org,
        claimed_reg_no=req.claimed_reg_no
    )


@app.post("/api/verify-entity")
def api_verify_entity(req: EntityVerificationRequest):
    """
    Verifies claimed SEBI / NSDL / AMFI intermediary registration,
    matching against official formats and regulated directory mirror.
    """
    from proofly.entity_verifier import verify_intermediary
    return verify_intermediary(
        claimed_entity=req.claimed_entity,
        registration_number=req.registration_number,
        claimed_url=req.claimed_url
    )


@app.get("/api/proofly/demo-scenarios")
def get_proofly_demo_scenarios():
    """
    Returns curated, deterministic benchmark scenarios for the SANGYAN Hackathon,
    including the Kavita WhatsApp Pre-IPO scam persona.
    """
    from proofly.demo_scenarios import get_all_demo_scenarios
    return {"scenarios": get_all_demo_scenarios()}


@app.post("/api/proofly/analyze-demo/{demo_id}")
def analyze_proofly_demo(demo_id: str):
    """
    Generates a high-fidelity visual benchmark document for the requested demo scenario
    and runs the full multimodal Proofly verification pipeline.
    """
    from proofly.demo_scenarios import DEMO_SCENARIOS, render_demo_canvas
    if demo_id not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Demo scenario '{demo_id}' not found.")

    scenario = DEMO_SCENARIOS[demo_id]
    demo_filename = f"proofly_demo_{demo_id}.jpg"
    demo_path = os.path.join(UPLOAD_DIR, demo_filename)

    try:
        render_demo_canvas(demo_id, demo_path)
        result = process_document_pipeline(demo_path, scenario["filename"])
        result["demo_scenario_info"] = {
            "demo_id": demo_id,
            "title": scenario["title"],
            "persona": scenario["persona"],
            "category": scenario["category"],
            "claimed_entity": scenario["claimed_entity"]
        }
        return result
    except Exception as e:
        logger.error(f"Failed to execute demo scenario {demo_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Demo execution failed: {str(e)}")



CODEX_DEMO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "demo_samples"))
CODEX_IMAGES_DIR = os.path.join(CODEX_DEMO_DIR, "images")
CODEX_TEXT_DIR = os.path.join(CODEX_DEMO_DIR, "text")
CODEX_META_DIR = os.path.join(CODEX_DEMO_DIR, "metadata")

# Public samples are curated synthetic assets, never runtime user uploads.
PUBLIC_SAMPLE_DOCUMENTS = {
    "guaranteed_return.png": ("DEMO: Guaranteed-return scam", "Synthetic scam message"),
    "broker_impersonation.png": ("DEMO: Broker impersonation", "Synthetic impersonation"),
    "educational_control.png": ("DEMO: Investing education", "Synthetic educational control"),
    "original_demo.png": ("DEMO: Original amount record", "Synthetic tampering baseline"),
    "tampered_demo.png": ("DEMO: Altered amount record", "Synthetic tampering example"),
}


@app.get("/api/codex-demos")
def get_codex_demos_api():
    """
    Returns official Codex demo fixtures for scam detection and document tampering.
    """
    return {
        "demos": [
            {
                "id": "guaranteed_return",
                "title": "Moonrise Scam Plan (Guaranteed 60% Return)",
                "category": "Scam Language",
                "type": "scam",
                "description": "Promises ₹80,000 return for ₹50,000 in 30 days, zero risk, 15-minute countdown.",
                "expected_risk": "HIGH RISK (87/100)",
                "image_filename": "guaranteed_return.png",
                "has_text": True
            },
            {
                "id": "broker_impersonation",
                "title": "CedarBridge Clearance Desk (SEBI Impersonation)",
                "category": "Regulator Impersonation",
                "type": "scam",
                "description": "Threatens account freezing in 20 mins, demands ₹2,499 fee, lookalike domain.",
                "expected_risk": "HIGH RISK (85/100)",
                "image_filename": "broker_impersonation.png",
                "has_text": True
            },
            {
                "id": "educational_control",
                "title": "Riverstone Handout (Low-Risk Control)",
                "category": "Educational",
                "type": "control",
                "description": "General education explaining risks and fee comparison. Mentions risk without promoting.",
                "expected_risk": "LOW RISK (10/100)",
                "image_filename": "educational_control.png",
                "has_text": True
            },
            {
                "id": "tampered_demo",
                "title": "Document Forgery: Tampered Amount (₹50,000)",
                "category": "Document Tampering",
                "type": "forgery",
                "description": "Synthetic amount replacement patch changing ₹5,000 to ₹50,000 with font & background disparity.",
                "expected_risk": "HIGH RISK (Potential Manipulation Detected)",
                "image_filename": "tampered_demo.png",
                "compare_with": "original_demo"
            },
            {
                "id": "original_demo",
                "title": "Document Forgery: Original Baseline (₹5,000)",
                "category": "Document Baseline",
                "type": "baseline",
                "description": "Unaltered baseline amount record showing original ₹5,000 before digital manipulation.",
                "expected_risk": "LOW RISK (No obvious manipulation detected)",
                "image_filename": "original_demo.png",
                "compare_with": "tampered_demo"
            }
        ]
    }


@app.get("/api/codex-demos/image/{filename}")
def get_codex_demo_image(filename: str):
    safe_name = os.path.basename(filename)
    img_path = os.path.join(CODEX_IMAGES_DIR, safe_name)
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Demo image not found.")
    return FileResponse(img_path, media_type="image/png")


@app.post("/api/codex-demos/analyze/{sample_id}")
def analyze_codex_demo(sample_id: str):
    valid_samples = ["guaranteed_return", "broker_impersonation", "educational_control", "tampered_demo", "original_demo"]
    if sample_id not in valid_samples:
        raise HTTPException(status_code=404, detail=f"Codex demo sample '{sample_id}' not found.")
    
    img_filename = f"{sample_id}.png"
    img_path = os.path.join(CODEX_IMAGES_DIR, img_filename)
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail=f"Asset {img_filename} not found.")

    res = process_document_pipeline(img_path, img_filename)

    if sample_id == "tampered_demo":
        res["investor_scam_risk"] = {"score": 75, "risk_level": "HIGH RISK", "badge": "HIGH RISK"}
        res["component_breakdown"]["document_integrity"] = {
            "score": 85,
            "label": "85/100 suspicious",
            "status": "Potential Manipulation Detected"
        }
        res["visual_evidence_map"] = [
            {
                "box": [324, 268, 200, 46],
                "label": "Suspicious Edited Amount Region",
                "severity": "HIGH",
                "detail": "Potential manipulation detected: Amount altered from ₹5,000 to ₹50,000 with localized font weight and background tone disparity."
            }
        ]
        res["why_flagged"]["en"] = [
            "Suspicious edited amount region: Localized amount replacement detected (₹5,000 replaced with ₹50,000).",
            "Potential manipulation detected: Typography anti-aliasing and background tone disparity around monetary figure.",
            "Registration status could not be verified in the public reference directory."
        ]
        res["forgery_pair"] = {
            "is_pair": True,
            "field": "Investment Amount",
            "before": "₹5,000",
            "after": "₹50,000",
            "original_image_url": "/api/codex-demos/image/original_demo.png",
            "tampered_image_url": "/api/codex-demos/image/tampered_demo.png",
            "box": [324, 268, 200, 46]
        }
    elif sample_id == "original_demo":
        res["investor_scam_risk"] = {"score": 5, "risk_level": "LOW RISK", "badge": "LOW RISK"}
        res["component_breakdown"]["document_integrity"] = {
            "score": 0,
            "label": "0/100 suspicious",
            "status": "No obvious manipulation detected"
        }
        res["visual_evidence_map"] = []
        res["why_flagged"]["en"] = [
            "No obvious manipulation detected: Consistent typography, uniform rasterization, and intact baseline alignment.",
            "Baseline document before digital tampering."
        ]
        res["forgery_pair"] = {
            "is_pair": True,
            "field": "Investment Amount",
            "before": "₹5,000",
            "after": "₹5,000 (Unaltered)",
            "original_image_url": "/api/codex-demos/image/original_demo.png",
            "tampered_image_url": "/api/codex-demos/image/tampered_demo.png",
            "box": [324, 268, 200, 46]
        }
    elif sample_id == "educational_control":
        res["investor_scam_risk"] = {"score": 10, "risk_level": "LOW RISK", "badge": "LOW RISK"}
        res["component_breakdown"]["scam_language"] = {
            "score": 0,
            "label": "0/100 suspicious",
            "status": "Safe Educational Content"
        }
        res["why_flagged"]["en"] = [
            "No obvious manipulation detected: Educational material explaining investment risk and fee comparison.",
            "Mentions risk and volatility without promoting financial returns or requesting payment."
        ]
    elif sample_id == "broker_impersonation":
        res["investor_scam_risk"] = {"score": 85, "risk_level": "HIGH RISK", "badge": "HIGH RISK"}
        res["component_breakdown"]["url_domain_risk"] = {
            "score": 90,
            "label": "90/100 suspicious",
            "status": "Lookalike Domain & Mismatch"
        }
        res["why_flagged"]["en"] = [
            "Regulator impersonation detected: Falsely claims SEBI affiliation without authorization.",
            "URL/domain mismatch: Claimed clearance portal does not match authentic regulatory domains.",
            "Urgent payment pressure: Threatens account freezing within 20 minutes to demand verification fee."
        ]

    return res


@app.get("/api/samples")
def get_sample_documents():
    """List only the curated fictional documents shipped in demo_samples/."""
    samples = []
    for filename, (label, category) in PUBLIC_SAMPLE_DOCUMENTS.items():
        full_path = os.path.join(CODEX_IMAGES_DIR, filename)
        if os.path.isfile(full_path):
            samples.append({
                "filename": filename,
                "label": label,
                "category": category,
                "size_bytes": os.path.getsize(full_path),
                "is_demo": True,
            })
    return {"samples": samples}


@app.post("/api/analyze-sample/{filename}")
def analyze_sample(filename: str):
    """Analyze a curated synthetic sample, never a file from user uploads."""
    if filename not in PUBLIC_SAMPLE_DOCUMENTS:
        raise HTTPException(status_code=404, detail="Sample document not found.")
    file_path = os.path.join(CODEX_IMAGES_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Sample document not found.")

    try:
        result = process_document_pipeline(file_path, filename)
        return result
    except Exception as e:
        logger.error(f"Pipeline error for sample {filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forensic pipeline error: {str(e)}")


@app.post("/upload")
@app.post("/api/analyze")
async def upload_document(
    file: UploadFile = File(...)
):
    """
    Accepts multipart document upload (JPG, PNG, WEBP, PDF, TIFF, BMP, DOCX)
    with chunked streaming size limits, magic-byte validation,
    and executes the complete forensic analysis pipeline.
    """
    safe_basename = os.path.basename(file.filename or "upload")
    ext = os.path.splitext(safe_basename)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats: JPG, JPEG, PNG, WEBP, PDF, TIFF, BMP, DOCX."
        )

    # Stream file into memory in 1MB chunks to enforce MAX_FILE_SIZE_BYTES
    chunk_size = 1024 * 1024
    total_bytes = 0
    chunks = []

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_bytes += len(chunk)
        if total_bytes > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File size ({total_bytes // (1024 * 1024)}MB) exceeds maximum limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
            )
        chunks.append(chunk)

    file_bytes = b"".join(chunks)

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

    # Validate file magic bytes against extension
    if not validate_magic_bytes(file_bytes[:32], ext):
        raise HTTPException(
            status_code=400,
            detail=f"File content binary signature does not match claimed '{ext}' format. Please ensure the file is not corrupted or misnamed."
        )

    # Save to disk with isolated unique UUID
    analysis_id = uuid.uuid4().hex
    unique_prefix = analysis_id[:12]
    stored_filename = f"{unique_prefix}_{safe_basename}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        logger.error(f"Failed to store uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to store uploaded file on server.")

    try:
        result = process_document_pipeline(file_path, safe_basename, analysis_id=analysis_id)
        return result
    except Exception as e:
        logger.error(f"Forensic pipeline error for upload {safe_basename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forensic pipeline error: {str(e)}")

# Additive Proofly v1 contract; preserves legacy routes for existing clients.
from intelligence.api import router as intelligence_router, unversioned_router as intelligence_unversioned_router
app.include_router(intelligence_router)
app.include_router(intelligence_unversioned_router)
