"""
Proofly Schema Adapter
Transforms internal multimodal pipeline and forensic results into the
standardized v1 Pydantic Analysis response model.
"""
from typing import Dict, Any, List, Optional, Tuple
import hashlib
from pathlib import Path
from intelligence.schema import (
    Analysis, Document, Assessment, Finding, SensitiveField,
    Claim, Destination, Identity, Evidence, Explanation
)

VALID_STATUSES = {'supported', 'partially_supported', 'conflicting', 'not_corroborated', 'unable_to_verify'}
VALID_LEVELS = {'LOW', 'MODERATE', 'HIGH'}


def normalize_bbox(raw_bbox: Any, max_w: int = 10000, max_h: int = 10000) -> Optional[Tuple[int, int, int, int]]:
    """
    Normalizes bounding boxes from either dict {'x','y','w','h'} or list/tuple
    to (x1, y1, x2, y2) with positive area and valid coordinates.
    """
    if not raw_bbox:
        return None

    try:
        if isinstance(raw_bbox, dict):
            x1 = max(0, int(raw_bbox.get('x', 0)))
            y1 = max(0, int(raw_bbox.get('y', 0)))
            w = max(1, int(raw_bbox.get('w', 10)))
            h = max(1, int(raw_bbox.get('h', 10)))
            x2 = min(max_w, x1 + w)
            y2 = min(max_h, y1 + h)
        elif isinstance(raw_bbox, (list, tuple)) and len(raw_bbox) == 4:
            x1 = max(0, int(raw_bbox[0]))
            y1 = max(0, int(raw_bbox[1]))
            x2 = max(x1 + 1, min(max_w, int(raw_bbox[2])))
            y2 = max(y1 + 1, min(max_h, int(raw_bbox[3])))
        else:
            return None

        if x2 <= x1:
            x2 = x1 + 1
        if y2 <= y1:
            y2 = y1 + 1

        return (x1, y1, x2, y2)
    except (ValueError, TypeError):
        return None


def pipeline_dict_to_analysis(
    doc_id: str,
    filename: str,
    pipeline_result: Dict[str, Any],
    file_bytes: Optional[bytes] = None
) -> Analysis:
    """
    Maps a combined pipeline output dictionary to the formal Analysis Pydantic schema.
    """
    proofly = pipeline_result.get("proofly", {})
    assessment_data = proofly.get("assessment", {})
    forgery = pipeline_result.get("forgery_analysis", {})
    plain = proofly.get("plain_explanations", {})
    pages = max(1, int(pipeline_result.get("total_pages", 1)))

    # 1. Assessment
    level = assessment_data.get("concern_level", pipeline_result.get("concern_level", "LOW"))
    if level not in VALID_LEVELS:
        level = "MODERATE" if level in ("MEDIUM", "SUSPICIOUS") else "LOW"

    raw_conf = forgery.get("confidence_score", pipeline_result.get("confidence_score", 85.0))
    conf = min(1.0, max(0.0, round(float(raw_conf) / 100.0 if raw_conf > 1.0 else float(raw_conf), 3)))

    summary = assessment_data.get(
        "status_label",
        pipeline_result.get("verdict") or f"{level.title()} verification concern."
    )

    assessment = Assessment(
        level=level,
        summary=summary,
        confidence=conf
    )

    # 2. Forensics (Findings)
    findings: List[Finding] = []
    visual_map = pipeline_result.get("visual_evidence_map", proofly.get("visual_evidence_map", []))

    for item in visual_map:
        bbox = normalize_bbox(item.get("bbox"))
        f_type = str(item.get("finding_type", "visual_anomaly"))
        expl = str(item.get("description", "Visual anomaly flagged during analysis."))
        f_conf = min(1.0, max(0.0, float(item.get("confidence", 0.65))))
        findings.append(Finding(
            type=f_type,
            page=1,
            bbox=bbox,
            confidence=f_conf,
            explanation=expl
        ))

    # 3. Sensitive Fields
    fields: List[SensitiveField] = []
    fin_fields = proofly.get("financial_fields", [])
    if isinstance(fin_fields, list):
        for f in fin_fields:
            if isinstance(f, dict):
                bbox = normalize_bbox(f.get("bbox"))
                fields.append(SensitiveField(
                    type=str(f.get("type", "field")),
                    value=str(f.get("value", "")),
                    page=1,
                    bbox=bbox,
                    confidence=min(1.0, max(0.0, float(f.get("confidence", 0.8)))),
                    concern=str(f.get("concern", ""))
                ))

    # 4. Claims & Evidence
    claims: List[Claim] = []
    raw_claims = proofly.get("claims", [])
    evidences: List[Evidence] = []

    if isinstance(raw_claims, list):
        for c in raw_claims:
            if isinstance(c, dict):
                bbox = normalize_bbox(c.get("bbox"))
                c_status = c.get("verification_status", "unable_to_verify")
                if c_status not in VALID_STATUSES:
                    c_status = "unable_to_verify"

                claim_evidences: List[Evidence] = []
                for ev in c.get("evidence", []):
                    if isinstance(ev, dict) and ev.get("source_url"):
                        rel = ev.get("relation", "unable_to_verify")
                        if rel not in VALID_STATUSES:
                            rel = "unable_to_verify"
                        qual = ev.get("source_quality", "unassessed")
                        if qual not in ("authoritative", "public", "unassessed"):
                            qual = "unassessed"
                        ev_item = Evidence(
                            source_url=str(ev.get("source_url", "")),
                            title=str(ev.get("title", "")),
                            retrieved_at=str(ev.get("retrieved_at", "2026-10-03")),
                            excerpt=str(ev.get("excerpt", "")),
                            entity=str(ev.get("entity", "")),
                            source_quality=qual,
                            relation=rel
                        )
                        claim_evidences.append(ev_item)
                        evidences.append(ev_item)

                claims.append(Claim(
                    text=str(c.get("text", "")),
                    category=str(c.get("category", "unspecified")),
                    page=1,
                    bbox=bbox,
                    confidence=min(1.0, max(0.0, float(c.get("confidence", 0.75)))),
                    extracted_entity=c.get("extracted_entity"),
                    verification_status=c_status,
                    evidence=claim_evidences
                ))

    # 5. Destinations (QR Codes & URLs)
    qr_codes: List[Destination] = []
    urls: List[Destination] = []

    for q in proofly.get("qr_analysis", []):
        if isinstance(q, dict):
            bbox = normalize_bbox(q.get("bbox"))
            qr_codes.append(Destination(
                value=str(q.get("data", q.get("value", ""))),
                domain=q.get("domain"),
                payment_identifier=q.get("payment_identifier", q.get("upi_id")),
                page=1,
                bbox=bbox,
                confidence=min(1.0, max(0.0, float(q.get("confidence", 1.0)))),
                concerns=list(q.get("concerns", []))
            ))

    for u in proofly.get("urls_analysis", []):
        if isinstance(u, dict):
            bbox = normalize_bbox(u.get("bbox"))
            urls.append(Destination(
                value=str(u.get("url", u.get("value", ""))),
                domain=u.get("domain"),
                payment_identifier=u.get("payment_identifier"),
                page=1,
                bbox=bbox,
                confidence=min(1.0, max(0.0, float(u.get("confidence", 0.9)))),
                concerns=list(u.get("concerns", []))
            ))

    # 6. Identities
    identities: List[Identity] = []
    id_data = proofly.get("identity_consistency", {})
    if isinstance(id_data, dict):
        for ent in id_data.get("entities", []):
            if isinstance(ent, dict):
                identities.append(Identity(
                    type=str(ent.get("type", "entity")),
                    value=str(ent.get("value", "")),
                    page=1,
                    inconsistencies=list(ent.get("inconsistencies", []))
                ))

    # 7. Safe Actions
    raw_safe_actions = plain.get("safe_steps", [])
    safe_actions: List[str] = []
    if isinstance(raw_safe_actions, list):
        for act in raw_safe_actions:
            if isinstance(act, dict):
                title = act.get("title", "").strip()
                action = act.get("action", "").strip()
                if title and action:
                    safe_actions.append(f"{title}: {action}")
                elif action:
                    safe_actions.append(action)
                elif title:
                    safe_actions.append(title)
            elif isinstance(act, str) and act.strip():
                safe_actions.append(act.strip())

    if not safe_actions:
        safe_actions = [
            "Verify the issuer using independently obtained contact details.",
            "Confirm payment identifiers before sending money.",
            "Do not follow document links until their destination is independently checked."
        ]

    # 8. Plain Explanations
    en_expl = plain.get("simple_explanation_en", summary)
    hi_expl = plain.get("simple_explanation_hi", f"सत्यापन की चिंता: {level}। कृपया विवरण स्वतंत्र रूप से जाँचें।")
    explanation = Explanation(en=en_expl, hi=hi_expl)

    # 9. Technical Details
    sha256 = hashlib.sha256(file_bytes).hexdigest() if file_bytes else ""
    tech_details = {
        "sha256": sha256,
        "document_type": pipeline_result.get("document_type"),
        "ocr_confidence": pipeline_result.get("ocr_confidence"),
        "risk_score": forgery.get("risk_score"),
        "risk_level": forgery.get("risk_level"),
        "authenticity_status": pipeline_result.get("authenticity_status"),
        "ela_details": forgery.get("ela_analysis", {}),
        "noise_details": forgery.get("noise_analysis", {}),
        "metadata_forensics": forgery.get("metadata_forensics", {}),
        "voice_script_en": plain.get("voice_script_en", ""),
        "voice_script_hi": plain.get("voice_script_hi", "")
    }

    return Analysis(
        schema_version="1.0",
        document=Document(id=doc_id, filename=filename, pages=pages),
        assessment=assessment,
        forensics=findings,
        sensitive_fields=fields,
        claims=claims,
        qr_codes=qr_codes,
        urls=urls,
        identities=identities,
        evidence=evidences,
        safe_actions=safe_actions,
        simple_explanation=explanation,
        technical_details=tech_details
    )
