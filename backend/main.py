import os
import shutil
import uuid
import logging
from typing import Optional, List, Dict, Any, Tuple
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

def process_document_pipeline(file_path: str, original_filename: str) -> Dict[str, Any]:
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

        return {
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
        }

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
        "message": "Document Forgery AI is running!",
        "version": "2.1.0",
        "supported_formats": ["JPG", "JPEG", "PNG", "WEBP", "PDF", "TIFF", "BMP", "DOCX"],
        "tesseract": pytesseract.pytesseract.tesseract_cmd
    }


@app.get("/api/health")
def health_check():
    tess_available = os.path.exists(pytesseract.pytesseract.tesseract_cmd)
    return {
        "status": "HEALTHY",
        "ocr_available": tess_available,
        "tesseract_path": pytesseract.pytesseract.tesseract_cmd,
        "upload_dir_configured": bool(UPLOAD_DIR),
        "supported_formats": ["JPG", "JPEG", "PNG", "WEBP", "PDF", "TIFF", "BMP", "DOCX"],
        "max_file_size_mb": MAX_FILE_SIZE_BYTES // (1024 * 1024)
    }


@app.get("/api/samples")
def get_sample_documents():
    """
    Returns preloaded sample documents from uploads/ for instant testing in the UI.
    Excludes temporary rendered files and non-document formats.
    """
    samples = []
    metadata_map = {
        "1.jpg": {"label": "Student ID Card", "category": "ID"},
        "id.jpg": {"label": "College ID (Bhagwan Parshuram)", "category": "ID"},
        "adhar raj.jpg": {"label": "Aadhaar Card (Raj Salonia)", "category": "Government ID"},
        "raj bank.jpg": {"label": "Bank Mandate Form", "category": "Banking"},
        "10 result.jpg": {"label": "CBSE Marksheet (Class 10)", "category": "Academic"},
        "RAJ 12.pdf": {"label": "Class 12 Certificate (PDF)", "category": "Academic PDF"},
        "Screenshot 2026-08-13 135707.png": {"label": "Digital Document Screenshot", "category": "Digital Screenshot"},
        "test.jpg": {"label": "Scanned Document", "category": "Generic"},
    }

    allowed_exts = tuple(SUPPORTED_EXTENSIONS)

    if os.path.exists(UPLOAD_DIR):
        for fname in os.listdir(UPLOAD_DIR):
            if fname.startswith(".") or fname.endswith(("_page1.jpg", "_converted.jpg", "_docx_preview.jpg", ".tmp")):
                continue
            if not fname.lower().endswith(allowed_exts):
                continue
            full_path = os.path.join(UPLOAD_DIR, fname)
            if os.path.isfile(full_path):
                info = metadata_map.get(fname, {"label": fname, "category": "General"})
                samples.append({
                    "filename": fname,
                    "label": info["label"],
                    "category": info["category"],
                    "size_bytes": os.path.getsize(full_path),
                    "is_demo": True
                })

    return {"samples": samples}


@app.post("/api/analyze-sample/{filename}")
def analyze_sample(filename: str):
    """
    Analyzes an existing sample document in uploads/ without requiring a re-upload.
    """
    safe_filename = os.path.basename(filename)
    if not safe_filename or safe_filename.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid filename requested.")

    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"Sample document '{safe_filename}' not found.")

    try:
        result = process_document_pipeline(file_path, safe_filename)
        return result
    except Exception as e:
        logger.error(f"Pipeline error for sample {safe_filename}: {e}", exc_info=True)
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
    unique_prefix = uuid.uuid4().hex[:12]
    stored_filename = f"{unique_prefix}_{safe_basename}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        logger.error(f"Failed to store uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to store uploaded file on server.")

    try:
        result = process_document_pipeline(file_path, safe_basename)
        return result
    except Exception as e:
        logger.error(f"Forensic pipeline error for upload {safe_basename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forensic pipeline error: {str(e)}")

# Additive Proofly v1 contract; preserves legacy routes for existing clients.
from intelligence.api import router as intelligence_router
app.include_router(intelligence_router)
