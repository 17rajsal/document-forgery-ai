"""
Proofly Master Pipeline Coordinator
Orchestrates the complete multimodal financial verification pipeline:
- Base document forensics (ELA, noise variance, copy-move, EXIF)
- Deep learning inference
- AI inpainting and generative erase detection
- Critical financial field tampering
- High-risk claim and scam language extraction
- Regulatory evidence verification
- QR code and URL inspection
- Identity consistency analysis
- Multimodal evidence fusion
- Plain-language & Bharat-first bilingual explanations
- Visual Evidence Map overlay coordinates
"""

import os
import re
import uuid
import datetime
import hashlib
from typing import Dict, Any, List, Optional
from PIL import Image
import numpy as np

from .qr_url_analyzer import detect_and_decode_qrcodes, extract_and_analyze_urls_from_text
from .ai_erase_detector import detect_ai_erase_and_inpainting
from .financial_field_analyzer import analyze_financial_fields
from .claim_extractor import extract_claims_from_text
from .evidence_checker import verify_claims_against_evidence
from .identity_consistency import build_entity_graph
from .entity_verifier import verify_intermediary
from .fusion_engine import fuse_proofly_evidence
from .plain_explainer import generate_plain_explanations


def build_visual_evidence_map(
    ai_inpainting_res: Dict[str, Any],
    financial_fields_res: Dict[str, Any],
    claims_res: List[Dict[str, Any]],
    qr_res: List[Dict[str, Any]],
    identity_res: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Synthesizes color-coded interactive visual evidence bounding boxes:
      - RED (manipulation): AI erase, spliced numbers, altered amounts
      - ORANGE (risk_claim): Guaranteed returns, FOMO urgency, payment pressure
      - YELLOW (payment_channel): QR codes, UPI handles, payment links
      - BLUE (regulatory_identity): SEBI/RBI claims, company headers, registration IDs
    """
    visual_boxes = []
    box_id = 1

    # 1. RED BOXES: AI Inpainting / Erase Regions
    for region in ai_inpainting_res.get("candidate_regions", []):
        if region.get("bbox"):
            visual_boxes.append({
                "id": f"box_{box_id}",
                "color": "red",
                "badge": "Digital Manipulation / Inpainting",
                "label": "Possible Reconstructed Region",
                "text_snippet": "Localized image patch",
                "bbox": region["bbox"],
                "severity": region.get("severity", "HIGH"),
                "reason": region.get("finding"),
                "explanation": region.get("explanation")
            })
            box_id += 1

    # 2. RED BOXES: Tampered Sensitive Fields
    for field in financial_fields_res.get("tampered_fields", []):
        if field.get("bbox"):
            visual_boxes.append({
                "id": f"box_{box_id}",
                "color": "red",
                "badge": "Altered Financial Field",
                "label": f"Altered {field.get('field_type', 'Field').replace('_', ' ').title()}",
                "text_snippet": field.get("raw_text", ""),
                "bbox": field["bbox"],
                "severity": "CRITICAL",
                "reason": "Typography anti-aliasing or patch background disparity",
                "explanation": (
                    "The sharpness, baseline, and noise texture around this specific number "
                    "differ significantly from the document's global background."
                )
            })
            box_id += 1

    # 3. ORANGE BOXES: High-Risk Financial Claims & Social Engineering
    for claim in claims_res:
        if claim.get("bbox"):
            visual_boxes.append({
                "id": f"box_{box_id}",
                "color": "orange",
                "badge": "High-Risk Claim",
                "label": claim.get("title", "High-Risk Financial Language"),
                "text_snippet": claim.get("exact_text", ""),
                "bbox": claim["bbox"],
                "severity": claim.get("severity", "HIGH"),
                "reason": claim.get("title"),
                "explanation": claim.get("explanation"),
                "verification_source": claim.get("verification_source")
            })
            box_id += 1

    # 4. YELLOW BOXES: QR Codes and Payment Endpoints
    for qr in qr_res:
        if qr.get("bbox"):
            pa = qr.get("upi_details", {}).get("payee_address") if qr.get("is_upi") else None
            visual_boxes.append({
                "id": f"box_{box_id}",
                "color": "yellow",
                "badge": "Payment Endpoint (QR)",
                "label": "Payment QR Code Destination",
                "text_snippet": pa or qr.get("raw_content", "")[:35],
                "bbox": qr["bbox"],
                "severity": "CRITICAL" if (qr.get("is_upi") and qr.get("upi_details", {}).get("is_personal_handle")) else "MODERATE",
                "reason": "Direct money transfer destination embedded in document",
                "explanation": (
                    f"Directs payment to {pa or 'linked website'}. "
                    "Investors should always verify whether this matches an authorized corporate clearing account."
                )
            })
            box_id += 1

    # 5. BLUE BOXES: Regulatory Claims & Identity Headers
    for field in financial_fields_res.get("all_fields", []):
        if field.get("field_type") == "REGULATORY_LICENSE_ID" and field.get("bbox"):
            visual_boxes.append({
                "id": f"box_{box_id}",
                "color": "blue",
                "badge": "Regulatory Identifier",
                "label": "Claimed SEBI / Statutory Registration",
                "text_snippet": field.get("raw_text", ""),
                "bbox": field["bbox"],
                "severity": "MODERATE",
                "reason": "Entity cites statutory market registration number",
                "explanation": (
                    "Verify this registration directly on sebi.gov.in. "
                    "Unauthorized channels frequently paste genuine registration numbers of unrelated entities."
                )
            })
            box_id += 1

    return visual_boxes


def run_proofly_pipeline(
    image: Image.Image,
    file_path: str,
    original_filename: str,
    extracted_text: str,
    ocr_words: List[Dict[str, Any]],
    base_forgery_analysis: Dict[str, Any],
    document_type: str
) -> Dict[str, Any]:
    """
    Executes all Proofly multimodal safety modules and synthesizes the full dossier.
    """
    # Compute SHA-256 for integrity auditing
    sha256_hash = "Unavailable"
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                sha256_hash = hashlib.sha256(f.read()).hexdigest()
        except Exception:
            pass

    # 1. QR Code Analysis
    qr_analysis = detect_and_decode_qrcodes(image)

    # 2. URL Analysis from Text
    urls_analysis = extract_and_analyze_urls_from_text(extracted_text)

    # 3. Identity Consistency Engine
    identity_analysis = build_entity_graph(
        extracted_text,
        qr_codes=qr_analysis,
        urls=urls_analysis
    )

    claimed_entity = identity_analysis.get("entity_map", {}).get("claimed_organization")

    # 4. AI Erase & Inpainting Detection
    ai_inpainting_analysis = detect_ai_erase_and_inpainting(image)

    # 5. Sensitive Financial Field Analysis
    financial_fields_analysis = analyze_financial_fields(
        text=extracted_text,
        words=ocr_words,
        image_input=image
    )

    # 6. High-Risk Claim & Scam Language Extraction
    claims_analysis = extract_claims_from_text(
        text=extracted_text,
        words=ocr_words,
        claimed_entity=claimed_entity
    )

    # 7. Regulatory Reality & Evidence Verification
    evidence_analysis = verify_claims_against_evidence(
        claims_analysis,
        financial_fields_analysis
    )

    # 8. Multi-Signal Evidence Fusion
    fusion_assessment = fuse_proofly_evidence(
        base_forensics=base_forgery_analysis,
        ai_inpainting_res=ai_inpainting_analysis,
        financial_fields_res=financial_fields_analysis,
        claims_res=claims_analysis,
        evidence_res=evidence_analysis,
        qr_res=qr_analysis,
        urls_res=urls_analysis,
        identity_res=identity_analysis
    )

    # 9. Plain-Language & Bharat-First Bilingual Explainer
    plain_explanations = generate_plain_explanations(
        assessment=fusion_assessment,
        claims=claims_analysis,
        financial_fields=financial_fields_analysis,
        identity_res=identity_analysis,
        qr_res=qr_analysis,
        ai_inpainting_res=ai_inpainting_analysis
    )

    # 10. Interactive Visual Evidence Map Boxes
    visual_evidence_map = build_visual_evidence_map(
        ai_inpainting_res=ai_inpainting_analysis,
        financial_fields_res=financial_fields_analysis,
        claims_res=claims_analysis,
        qr_res=qr_analysis,
        identity_res=identity_analysis
    )

    # 11. Regulatory Entity & Registration Number Verification
    reg_number = None
    reg_match = re.search(r"\b(?:INZ\d{9}|INA\d{9}|INH\d{9}|INP\d{9}|IN-DP-\d{3}-\d{4}|ARN[- ]?\d{4,8})\b", extracted_text, re.I)
    if reg_match:
        reg_number = reg_match.group(0).strip()

    entity_verification_res = verify_intermediary(
        claimed_entity=claimed_entity,
        registration_number=reg_number
    )

    # 12. Explainable 4-Component Investor Scam Risk Scoring
    base_score = int(base_forgery_analysis.get("risk_score", 0))
    doc_integrity_score = min(100, int(base_score * 0.6 + (35 if ai_inpainting_analysis.get("anomaly_detected") else 0) + (30 if financial_fields_analysis.get("has_tampered_fields") else 0)))

    has_crit_claim = any(c.get("severity") == "CRITICAL" for c in claims_analysis)
    has_high_claim = any(c.get("severity") == "HIGH" for c in claims_analysis)
    scam_lang_score = 92 if has_crit_claim else 75 if has_high_claim else min(100, len(claims_analysis) * 25)

    has_upi_personal = any(q.get("is_personal_upi") for q in qr_analysis)
    has_lookalike_url = any(u.get("typosquatting_detected") for u in urls_analysis)
    has_suspicious_tld = any(u.get("has_suspicious_tld") for u in urls_analysis)
    if has_lookalike_url or has_upi_personal:
        url_domain_risk_score = 85
    elif has_suspicious_tld:
        url_domain_risk_score = 65
    elif urls_analysis or qr_analysis:
        url_domain_risk_score = 25
    else:
        url_domain_risk_score = 5

    entity_status = entity_verification_res.get("status", "UNABLE TO VERIFY")
    entity_risk = 90 if entity_status == "NOT VERIFIED" else 50 if entity_status == "UNABLE TO VERIFY" and (claimed_entity or reg_number) else 5

    active_weights = [(doc_integrity_score, 0.35), (scam_lang_score, 0.35)]
    if urls_analysis or qr_analysis:
        active_weights.append((url_domain_risk_score, 0.15))
    if claimed_entity or reg_number:
        active_weights.append((entity_risk, 0.15))

    total_w = sum(w for _, w in active_weights)
    overall_investor_risk = int(sum(s * w for s, w in active_weights) / total_w)

    if has_crit_claim or has_upi_personal or entity_status == "NOT VERIFIED":
        overall_investor_risk = max(overall_investor_risk, 87)

    overall_tier = "HIGH RISK" if overall_investor_risk >= 65 else "MODERATE RISK" if overall_investor_risk >= 30 else "LOW RISK"

    why_flagged_en = []
    why_flagged_hi = []

    if has_crit_claim:
        why_flagged_en.append("Guaranteed-return language detected, directly violating SEBI Investment Adviser Regulations.")
        why_flagged_hi.append("Guaranteed return ka daawa paya gaya jo SEBI niyamavali ke virudh hai.")
    for tf in financial_fields_analysis.get("tampered_fields", []):
        why_flagged_en.append(f"{tf.get('raw_text')} amount/date region exhibits sharpness disparity and visual inconsistency.")
        why_flagged_hi.append(f"{tf.get('raw_text')} rashi/taareekh par local typography chhed-chhad ke sanket hain.")
    if has_upi_personal:
        why_flagged_en.append("QR destination routes funds to a personal UPI handle instead of an authorized corporate account.")
        why_flagged_hi.append("QR code se payment vyaktigat UPI par ja raha hai, company account mein nahi.")
    if entity_status == "NOT VERIFIED":
        why_flagged_en.append(entity_verification_res.get("verdict", "Claimed registration number does not match entity."))
        why_flagged_hi.append("Registration number match nahi hua ya kisi doosri company ka nikla.")
    elif entity_status == "UNABLE TO VERIFY" and (claimed_entity or reg_number):
        why_flagged_en.append("Registration number could not be independently corroborated in official public directory.")
        why_flagged_hi.append("Registration number ki sarkari directory se pushti nahi ho saki.")
    if has_lookalike_url:
        why_flagged_en.append("Link domain mimics an authentic financial institution (lookalike / typosquat).")
        why_flagged_hi.append("Link kisi asli bank ya regulator jaisi nakli website ka hai.")

    if not why_flagged_en:
        why_flagged_en.append("No obvious digital manipulation, scam promises, or payment redirects detected.")
        why_flagged_hi.append("Is document mein koi spasht chhed-chhad ya dhokhadhadi ke sanket nahi paye gaye.")

    # Structured Proofly Output Dossier
    proofly_dossier = {
        "proofly_version": "1.0.0",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "file_hash_sha256": sha256_hash,
        "investor_scam_risk": {
            "score": overall_investor_risk,
            "risk_level": overall_tier,
            "badge": overall_tier
        },
        "component_breakdown": {
            "document_integrity": {
                "score": doc_integrity_score,
                "label": f"{doc_integrity_score}/100 suspicious",
                "status": "High Anomaly" if doc_integrity_score >= 60 else "Moderate" if doc_integrity_score >= 25 else "Clean"
            },
            "scam_language": {
                "score": scam_lang_score,
                "label": f"{scam_lang_score}/100 suspicious",
                "status": "High Risk" if scam_lang_score >= 60 else "Moderate" if scam_lang_score >= 25 else "Clean",
                "claims_count": len(claims_analysis)
            },
            "url_domain_risk": {
                "score": url_domain_risk_score,
                "label": f"{url_domain_risk_score}/100 suspicious" if (urls_analysis or qr_analysis) else "Not Found",
                "status": "High Risk" if url_domain_risk_score >= 60 else "Moderate" if url_domain_risk_score >= 25 else "Safe",
                "has_personal_upi": has_upi_personal
            },
            "entity_verification": {
                "status": entity_status,
                "verdict": entity_verification_res.get("verdict"),
                "claimed_entity": entity_verification_res.get("claimed_entity"),
                "claimed_registration": entity_verification_res.get("claimed_registration"),
                "matched_record": entity_verification_res.get("matched_record")
            }
        },
        "why_flagged": {
            "en": why_flagged_en,
            "hi": why_flagged_hi
        },
        "assessment": fusion_assessment,
        "plain_explanations": plain_explanations,
        "visual_evidence_map": visual_evidence_map,
        "ai_inpainting": ai_inpainting_analysis,
        "financial_fields": financial_fields_analysis,
        "claims": claims_analysis,
        "evidence_verification": evidence_analysis,
        "qr_analysis": qr_analysis,
        "urls_analysis": urls_analysis,
        "identity_consistency": identity_analysis,
        "entity_verification": entity_verification_res,
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

    return sanitize_for_json(proofly_dossier)
