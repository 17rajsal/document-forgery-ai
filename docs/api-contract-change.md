# Proofly intelligence contract proposal and integration decision

The existing `POST /api/analyze` and `/upload` return a legacy document report.
Replacing that response would break the concurrently developed frontend. Preserve
both routes and introduce `POST /api/v1/analyze`, `GET /api/v1/analysis/{id}`,
`GET /api/v1/analysis/{id}/technical`, and `GET /api/v1/analysis/{id}/report-data`.
The versioned response is defined by `backend/intelligence/schema.py` and exposed
in OpenAPI. Frontend adapters can explicitly opt into v1. No legacy field is renamed.

Coordinates are `[x1,y1,x2,y2]` in rendered page pixels, pages are one-based.
Unknown localization is null, never a made-up rectangle. Confidence is [0,1],
an uncalibrated signal strength, not a probability of fraud. OCR and coverage live
in technical_details; incomplete analysis is explicit. LOW never asserts authenticity.
Evidence lookup without a configured source corpus returns unable_to_verify.
Stored reports are local JSON; production authentication and retention must be
provided by the deployment. This additive API is intended for trusted local use.
