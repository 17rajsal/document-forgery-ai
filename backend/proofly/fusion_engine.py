"""
Proofly Multi-Signal Evidence Fusion Engine
Synthesizes signals across physical forensics, AI inpainting detection,
financial field tampering, high-risk claims, evidence checking, QR/URL analysis,
and identity consistency into an explainable assessment.

Concern Levels:
- LOW: Document exhibits normal physical characteristics, no critical field tampering, and standard claims.
- MODERATE: Isolated anomalies detected (e.g. compression artifacts or unverified entity claim) requiring caution.
- HIGH: Multiple corroborating red flags (e.g. tampered amount + guaranteed return claim + personal UPI QR).
"""

from typing import Dict, Any, List, Optional


def fuse_proofly_evidence(
    base_forensics: Dict[str, Any],
    ai_inpainting_res: Dict[str, Any],
    financial_fields_res: Dict[str, Any],
    claims_res: List[Dict[str, Any]],
    evidence_res: List[Dict[str, Any]],
    qr_res: List[Dict[str, Any]],
    urls_res: List[Dict[str, Any]],
    identity_res: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fuses multimodal signals into an explainable Proofly Assessment.
    """
    risk_points = 0
    key_findings = []
    category_summary = {}

    # 1. Base Forensic Signals (ELA, Noise, Copy-Move, EXIF)
    base_score = base_forensics.get("risk_score", 0)
    if base_score >= 60:
        risk_points += 25
        key_findings.append({
            "title": "Document Compression & Pixel Inconsistency",
            "detail": "Physical pixel error levels and noise profiles show anomalies consistent with localized editing.",
            "severity": "HIGH",
            "source": "Forensic Engine"
        })
    elif base_score >= 35:
        risk_points += 12
        key_findings.append({
            "title": "Minor Forensic Variation",
            "detail": "Localized compression or scanner variations detected. May reflect re-saving or light editing.",
            "severity": "MODERATE",
            "source": "Forensic Engine"
        })

    # 2. AI Erase / Inpainting Signals
    if ai_inpainting_res.get("inpainting_detected"):
        risk_points += 28
        key_findings.append({
            "title": "Potential AI Erase or Reconstructed Region",
            "detail": f"{ai_inpainting_res.get('regions_count', 1)} region(s) exhibit synthetic smoothing and missing paper grain.",
            "severity": "CRITICAL",
            "source": "AI Inpainting Detector"
        })

    # 3. Critical Financial Field Tampering & Contradictions
    if financial_fields_res.get("semantic_contradictions"):
        risk_points += 35
        for contra in financial_fields_res["semantic_contradictions"]:
            key_findings.append({
                "title": contra["title"],
                "detail": contra["description"],
                "severity": "CRITICAL",
                "source": "Financial Field Analyzer"
            })

    if financial_fields_res.get("tampered_fields"):
        risk_points += 22
        key_findings.append({
            "title": "Financial Field Boundary Anomaly",
            "detail": f"{len(financial_fields_res['tampered_fields'])} sensitive field(s) show typography or background discrepancies.",
            "severity": "HIGH",
            "source": "Financial Field Analyzer"
        })

    # 4. Financial Claims & Scam Language
    critical_claims = [c for c in claims_res if c.get("severity") == "CRITICAL"]
    high_claims = [c for c in claims_res if c.get("severity") == "HIGH"]

    if critical_claims:
        risk_points += min(35, len(critical_claims) * 18)
        for c in critical_claims[:3]:
            key_findings.append({
                "title": c["title"],
                "detail": f"Claim: \"{c['exact_text']}\" — {c['explanation']}",
                "severity": "CRITICAL",
                "source": "Financial Claims Engine"
            })
    elif high_claims:
        risk_points += min(20, len(high_claims) * 10)
        for c in high_claims[:2]:
            key_findings.append({
                "title": c["title"],
                "detail": f"Claim: \"{c['exact_text']}\" — {c['explanation']}",
                "severity": "HIGH",
                "source": "Financial Claims Engine"
            })

    # 5. Regulatory Evidence Checking
    conflicting_ev = [e for e in evidence_res if e.get("evidence_status") == "Conflicting evidence"]
    if conflicting_ev:
        risk_points += 25
        key_findings.append({
            "title": "Claims Contradict Regulatory Mandates",
            "detail": f"{len(conflicting_ev)} statement(s) directly conflict with statutory SEBI / RBI market rules.",
            "severity": "CRITICAL",
            "source": "Evidence Checker"
        })

    # 6. QR Code & URL Findings
    for qr in qr_res:
        for rf in qr.get("risk_flags", []):
            if rf.get("severity") == "CRITICAL":
                risk_points += 30
            else:
                risk_points += 12
            key_findings.append({
                "title": rf["title"],
                "detail": rf["description"],
                "severity": rf.get("severity", "HIGH"),
                "source": "QR Code Inspector"
            })

    for u in urls_res:
        for rf in u.get("risk_flags", []):
            if rf.get("severity") == "CRITICAL":
                risk_points += 25
            else:
                risk_points += 10
            key_findings.append({
                "title": rf["title"],
                "detail": rf["description"],
                "severity": rf.get("severity", "HIGH"),
                "source": "URL Analyzer"
            })

    # 7. Identity Consistency Findings
    if not identity_res.get("is_consistent", True):
        for mm in identity_res.get("mismatches", []):
            risk_points += 25
            key_findings.append({
                "title": mm["title"],
                "detail": mm["description"],
                "severity": mm.get("severity", "CRITICAL"),
                "source": "Identity Consistency Engine"
            })

    # Determine Concern Level
    # LOW: < 30
    # MODERATE: 30 - 64
    # HIGH: >= 65
    if risk_points >= 65 or len([k for k in key_findings if k["severity"] == "CRITICAL"]) >= 2:
        concern_level = "HIGH"
        status_label = "Verification Concern: High"
    elif risk_points >= 30 or len([k for k in key_findings if k["severity"] in ("CRITICAL", "HIGH")]) >= 1:
        concern_level = "MODERATE"
        status_label = "Verification Concern: Moderate"
    else:
        concern_level = "LOW"
        status_label = "Verification Concern: Low"

    # Category Summary Counts
    category_summary = {
        "document_manipulation": "Concern Detected" if base_score >= 60 else "No Strong Anomaly",
        "ai_inpainting_detected": "Possible Inpainting / Erase" if ai_inpainting_res.get("inpainting_detected") else "None Detected",
        "critical_fields_flagged": len(financial_fields_res.get("tampered_fields", [])) + len(financial_fields_res.get("semantic_contradictions", [])),
        "high_risk_claims": len(claims_res),
        "identity_mismatches": identity_res.get("mismatch_count", 0),
        "qr_and_urls_flagged": len([rf for qr in qr_res for rf in qr.get("risk_flags", [])]) + len([rf for u in urls_res for rf in u.get("risk_flags", [])]),
        "evidence_conflicts": len(conflicting_ev)
    }

    return {
        "concern_level": concern_level,
        "status_label": status_label,
        "total_risk_score": min(100, risk_points),
        "key_findings": key_findings,
        "category_summary": category_summary,
        "why_am_i_seeing_this": [k["detail"] for k in key_findings[:5]],
        "disclaimer": (
            "Proofly provides evidence-based document inspection and does not provide investment advice, "
            "buy/sell signals, price predictions, or guaranteed legal fraud determinations. "
            "These findings highlight specific technical and textual elements that warrant independent verification."
        )
    }
