# Proofly backend intelligence handoff

Implemented on `feature/proofly-ai-backend`. Frontend files and the pre-existing
uncommitted `backend/proofly/` prototype are outside this change. The stable engine
is `backend/intelligence/`; it does not use prototype regulatory rules as evidence.

## Architecture and existing-system audit

Existing backend: FastAPI in `backend/main.py`; upload validation, PDFium, Pillow,
Tesseract multi-pass OCR, document classification and domain field extraction.
Existing `forgery_detector.py`: JPEG ELA, noise variance, ORB copy-move, text layout,
metadata and weighted risk scoring. The new engine reuses ELA, noise and ORB, but
uses concern-family fusion instead of the legacy authenticity verdicts.
Existing ML: binary MobileNetV3-small / optional ResNet18 in `train.py`, checkpoint
in `models/document_forgery_model.pth`, inference in `infer.py` and `ml_detector.py`.
Existing calibration: `backend/train_model.py`; dataset generation and grouping:
`backend/generate_dataset.py`, `backend/dataset_manager.py`. Existing evaluation:
`evaluate.py`, `backend/evaluate_model.py`, `outputs/evaluation_results.json`.
Legacy API: `/upload`, `/api/analyze`, `/api/analyze-sample/{filename}`,
`/api/samples`, `/api/health` (other agent may extend these).

New pipeline: bounded page decoding -> OCR with original rendered coordinates ->
span-localized fields/claims -> independent visual checks -> passive QR/URL
inspection -> contact/payment consistency -> curated evidence retrieval -> concern
fusion -> English/Hindi explanation -> validated JSON persistence.

Visual model: neighbor-matched residual/noise/compression heuristics, page-level
ELA/noise/ORB and limited text-height/baseline comparison. Possible reconstruction
is a low-confidence hypothesis, not proof of AI erase. Correlated visual detectors
count as one family; repetitions of language do not increase the family count.
HIGH requires three families. An unavailable check reduces coverage; no usable
OCR prevents an unqualified LOW result. Confidence is not statistically calibrated.

## Endpoints and response schema

- `POST /api/v1/analyze`: multipart field `file`; image, screenshot, multipage TIFF,
  PDF. Maximum 30 MB, 20 pages, 12 million rendered pixels per page.
- `GET /api/v1/analysis/{id}`: persisted Analysis.
- `GET /api/v1/analysis/{id}/technical`: page dimensions, OCR text/words, confidence,
  detector availability, coverage, signal families, SHA-256 and limitations.
- `GET /api/v1/analysis/{id}/report-data`: same validated Analysis for report adapters.

`backend/intelligence/schema.py` is the source of truth;
`docs/proofly-schema.json` is its generated JSON Schema. Live OpenAPI: `/openapi.json`.
Top-level fields: schema_version, document, assessment, forensics, sensitive_fields,
claims, qr_codes, urls, identities, evidence, safe_actions, simple_explanation,
technical_details. Coordinates are `[x1,y1,x2,y2]`, in the page dimensions recorded
in technical_details. Page numbering starts at 1. Null bbox means unlocalized.
Confidence range is 0..1. Display LOW/MODERATE/HIGH as **verification concern**.
Field types include amount, percentage, date, account, phone, upi, registration,
reference, url, email, name and entity. Schema field names are stable within v1.
Legacy endpoints retain their response shape; decision recorded before implementation
in `docs/api-contract-change.md`. DOCX remains on the legacy route.

## Evidence and destination behavior

No user-document destination is fetched or opened. QR decoding exposes the exact
payload. URL checks include shorteners, credentials, IP literals, HTTP and IDN
lookalike review. Printed UPI vs QR destination and email vs website are compared.
A domain difference is an unverified affiliation, not proven impersonation.

Optional `PROOFLY_EVIDENCE_CORPUS` points to a curator-maintained JSON array:
`[{"claim_text":"exact extracted text","evidence":{"source_url":"https://...",
"title":"source title","retrieved_at":"ISO timestamp","excerpt":"actual excerpt",
"entity":"exact entity","source_quality":"authoritative","relation":"supported"}}]`.
The curator must supply genuine records and the actual relationship; the backend
never manufactures citations. HTTPS/excerpt checks and exact entity/claim matching
prevent unrelated source records from being reused. Authoritative records sort first.
Allowed relations: supported, partially_supported, conflicting, not_corroborated,
unable_to_verify. Missing, unreadable or invalid corpus / unidentified entity ->
unable_to_verify. No exact match in an available corpus -> not_corroborated, meaning
only absence from that corpus. Disagreeing records -> unable_to_verify. There is
no live web search, source freshness enforcement or automated entailment model.

## Dataset and training changes

Audit found 700 records / 100 source groups, with **58 source groups crossing splits**.
All 700 lack manipulation subtype labels; files exist and no exact file hashes cross
splits. `outputs/proofly_dataset_audit.json` contains the original audit.
Grouping now uses source identity independent of class label; it does not mutate
input records. Both old calibration and CNN training have provenance/leakage gates.
ImageFolder training also rejects images absent from the source manifest.

`intelligence.synthetic` generates original, edited image, mask and JSON metadata
for text, amount, date, account, QR, URL, phone, percentage, registration and a simple
logo replacement; it also generates classical Telea inpainting, recompression and
low-resolution examples. Source hashes determine splits. Recompression/resizing
are benign degradation controls. AI erase/generative fill must be imported with
`import_ai_edit(original, edited, mask, output, kind, provenance)`; classical
inpainting is never mislabeled as generative AI. Demo output is under
`outputs/proofly_synthetic/`, not used to claim generalization.

A separately trained experimental baseline uses six image statistics and L2 logistic
regression, standardized with training data only. Source grouping gives 420 train,
140 validation and 140 test images. Validation selected threshold 0.27 for F1;
the untouched test set produced:

| Metric | Test result |
|---|---:|
| Precision | 44.44% |
| Recall | 100.00% |
| F1 | 61.54% |
| False-positive rate | 93.75% |
| ROC-AUC | 0.5846 |
| TP / FP / TN / FN | 60 / 75 / 5 / 0 |

This baseline is unsuitable for production and **not enabled in API fusion**.
The corrected manifest, model, predictions and evaluation are in
`outputs/proofly_baseline/`. Existing CNN weights were not overwritten or retrained.
Saved legacy metrics (not rerun here): precision 51.89%, recall 78.41%, F1 62.45%,
559/1125 genuine false positives (49.69%). Their provenance is insufficient for a
claim of source-independent performance. Neither set is an end-to-end Proofly benchmark.
Per-manipulation metrics are available when labels exist; currently only unspecified
is reportable. Localization IoU is implemented but not reported without aligned
predictions/ground-truth masks. No fabricated metrics.

## Validation and known limitations

Regression suite covers repeated-span localization, negation, schema bounds, URL
parsing, evidence failures/exact binding, multipage processing, unavailable OCR,
blank-page forensics, leakage grouping, known metrics, upload/storage, file signature,
OpenAPI, detector isolation, calendar dates and edit-mask coverage. Generated two-page
PDF smoke test: both pages processed, 8 fields, 4 claims, OCR mean 0.9538 per page.
These fixtures validate behavior, not accuracy on real financial documents.

Limits: heuristic false positives; no validated AI-origin attribution; no reference
logo database; no comprehensive typography/anti-aliasing model; simple English-first
claim/field patterns with limited Hindi phrases; names and issuer attribution are
label-based; no full financial arithmetic contradiction engine; no domain ownership
or regulator registry integration; no payment-account ownership proof. Hindi output
is a concern summary, not a translation of each finding. PDF rasterization can
introduce compression/resampling signals. OCR failures can hide claims and fields.

Local JSON storage has no built-in user authentication, tenant isolation, expiry or
rate limiting. Use on a trusted local deployment; production service controls are
separate work. Upload temporary files are removed; persisted reports retain OCR text.

## Setup and integration

From repository root, PowerShell:

```powershell
.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
$env:PYTHONPATH='backend'
# Install Tesseract separately; main.py resolves TESSERACT_CMD or the usual Windows path.
# Optional Hindi OCR requires installed hin language data:
# $env:PROOFLY_OCR_LANG='eng+hin'
.venv/Scripts/python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Tests and reproducible audit/training:

```powershell
$env:PYTHONPATH='backend'
.venv/Scripts/python.exe -m unittest backend/test_intelligence.py -v
.venv/Scripts/python.exe backend/intelligence/training.py dataset/manifest.csv --root dataset --output outputs/proofly_dataset_audit.json
.venv/Scripts/python.exe -m intelligence.train_baseline dataset/manifest.csv dataset outputs/proofly_baseline
.venv/Scripts/python.exe -m intelligence.synthetic dataset/docs/id_card_020_orig.jpg outputs/proofly_synthetic --bbox 100 100 240 130
```

Frontend integration: opt into `/api/v1/analyze`; do not assume legacy prototype
fields exist. Scale boxes with each page's rendered width/height. Show missing
coverage, unavailable verification and null boxes explicitly. Do not relabel concern
confidence as fraud probability or claim LOW establishes authenticity. External links
should remain inert until a user elects to inspect them. Use report-data for report
rendering; English and Hindi summaries are at simple_explanation.en / .hi.

Files in this change: backend/intelligence/{schema,extraction,evidence,destinations,
forensics,engine,api,training,synthetic,train_baseline,__init__}.py;
backend/test_intelligence.py; backend/dataset_manager.py; backend/train_model.py;
train.py; additive router registration in backend/main.py; docs/api-contract-change.md;
docs/proofly-schema.json; this handoff; audit/baseline evaluation artifacts.
The other agent's frontend, integration, requirements and prototype edits are excluded.
