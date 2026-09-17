# Document Forgery AI - Enterprise Forensic & Neural OCR System

> **A multi-spectrum document tampering detection platform combining Computer Vision (Error Level Analysis, Noise Inconsistency, Copy-Move detection), OCR text extraction, and Algorithmic Checksum Verification with a modern React dashboard.**

---

## Architecture Overview

```
document-forgery-ai/
├── backend/
│   ├── main.py                # FastAPI REST API, dynamic OCR loader, PDF rasterizer, SPA mount
│   ├── forgery_detector.py    # Multi-format ELA, thermal heatmaps, noise variance, software traces, composite scoring
│   ├── field_extractor.py     # Regex & spatial extractors with Verhoeff checksum & format validators
│   ├── document_classifier.py # Keyword-heuristic document classifier
│   ├── requirements.txt       # Python dependencies (FastAPI, OpenCV, Pillow, PyPDFium2, PyTesseract)
│   ├── uploads/               # Document storage & preloaded forensic test suite
│   └── Dockerfile             # Multi-stage production container
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Enterprise Forensic Dashboard with Multi-Spectrum Visualizer
│   │   ├── index.css          # Tailwind CSS v4 design system
│   │   └── main.jsx           # React root
│   ├── vite.config.js         # Vite configuration with API proxy
│   └── package.json           # React 19, Tailwind CSS v4, Lucide React
├── docker-compose.yml         # Containerized 1-command deployment
├── run_app.bat                # Windows 1-click startup script
└── README.md                  # System documentation
```

---

## Key Features

### 1. Multi-Spectrum Digital Forensic Suite
- **Multi-Format Error Level Analysis (ELA)**: Recompresses input files across JPEG compression matrices to identify spliced pixels and altered text. Generates high-contrast difference maps and a **Thermal Jet Heatmap** for visual investigation.
- **Noise & Texture Inconsistency Detection**: Evaluates localized pixel noise variance across image tiles using high-pass Laplacian filtering to flag spliced elements pasted from external sources.
- **Copy-Move Duplication Detection**: Detects cloned signatures, stamps, and duplicated digits across separated document regions using ORB feature detection.
- **Deep Software Signature Forensics**: Inspects EXIF, XMP, and raw byte-streams for tampering software fingerprints: **Adobe Photoshop, GIMP, Canva, Photopea, PicsArt, Paint.NET, CorelDraw, and Acrobat Editors**.
- **Composite Risk Scoring Engine (0-100)**: Computes a unified risk score categorizing documents into:
  - **`AUTHENTIC`** (Score 0–25)
  - **`SUSPICIOUS`** (Score 26–55)
  - **`LIKELY FORGED / TAMPERED`** (Score 56–100)

### 2. Algorithmic Data Validation & OCR
- **PyTesseract Neural OCR**: Preprocesses images (contrast amplification, sharpening, LANCZOS upscaling) and captures word-level coordinates and confidence metrics.
- **Official Verhoeff Checksum Algorithm**: Mathematically validates 12-digit Indian Aadhaar numbers to immediately detect fabricated IDs.
- **Financial Format Validation**: Validates RBI IFSC codes (`[A-Z]{4}0[A-Z0-9]{6}`) and date sanity.
- **Native PDF Ingestion**: High-resolution rasterization using Google PDFium (`pypdfium2`), requiring no external poppler installation.

### 3. Professional Web Interface
- **Interactive Multi-View Inspector**: Toggle between Original Document, ELA Thermal Heatmap, Grayscale ELA Diff, and Noise Splicing Map with zoom and pan controls.
- **Preloaded Test Suite**: One-click instant testing on included sample IDs, marksheets, bank forms, and certificates.
- **Structured Fields Table**: Clean key-value presentation with copy-to-clipboard actions and verification badges.
- **Forensic Findings & Evidence Log**: Detailed severity-coded cards (`CRITICAL`, `WARNING`, `VERIFIED`, `INFO`) explaining the forensic rationale for every anomaly.

---

## Getting Started (Quick Run)

### Option 1: Direct Run on Windows
Double-click `run_app.bat` or execute in PowerShell:
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Open your browser at **`http://localhost:8000`**. The backend will automatically serve both the API and the React web dashboard.

### Option 2: Full-Stack Development Mode
1. **Start Backend**:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```
2. **Start Frontend Dev Server (Vite)**:
   ```bash
   cd frontend
   npm run dev
   ```
   Open **`http://localhost:5173`**.

### Option 3: Docker Deployment
```bash
docker-compose up --build
```

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the web dashboard (or API status if built frontend is absent) |
| `GET` | `/api/health` | System health, OCR availability, and Tesseract path |
| `GET` | `/api/samples` | List preloaded test documents available for immediate analysis |
| `POST` | `/api/analyze-sample/{filename}` | Run complete forensic pipeline on an existing sample document |
| `POST` | `/upload` or `/api/analyze` | Multipart upload (`file=@doc.pdf`) returning full forensic JSON report |

---

## Forensic Method Details

### Error Level Analysis (ELA)
When an image is edited, original regions degrade in quality at different rates than newly pasted or altered sections. ELA re-saves the image at quality 90 and calculates the difference:
$$\Delta(x, y) = |I_{\text{original}}(x, y) - I_{\text{recompressed}}(x, y)|$$
Tampered regions have distinct error levels, appearing prominently in the thermal Jet colormap.

### Noise Inconsistency
Scanned physical documents have uniform sensor noise and paper grain:
$$\sigma^2_{\text{tile}} = \frac{1}{N}\sum (L(x, y) - \mu)^2$$
Tiles exceeding $\mu_{\text{median}} + 2.5\sigma$ indicate digital splicing from disparate sources.
