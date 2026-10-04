"""
Proofly QR Code & URL Inspector
Extracts, decodes, and forensically analyzes QR codes and hyperlinked domains.
Detects UPI payment redirects, lookalike domains (typosquatting), and suspicious TLDs.
"""

import re
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np
from PIL import Image

# Known regulatory and premier financial domains in India
TRUSTED_FINANCIAL_DOMAINS = {
    "sebi.gov.in": "Securities and Exchange Board of India (SEBI)",
    "rbi.org.in": "Reserve Bank of India (RBI)",
    "bseindia.com": "Bombay Stock Exchange (BSE)",
    "nseindia.com": "National Stock Exchange of India (NSE)",
    "scores.gov.in": "SEBI Complaints Redress System (SCORES)",
    "sachet.rbi.org.in": "RBI Sachet Portal",
    "cybercrime.gov.in": "National Cyber Crime Reporting Portal",
    "incometax.gov.in": "Income Tax Department of India",
}

# Suspicious TLDs commonly seen in phishing and social engineering
SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".club", ".online", ".site", ".cc", ".tk", ".work",
    ".vip", ".buzz", ".fit", ".rest", ".live", ".space", ".link", ".click"
}

# Common link shorteners used to conceal destination URLs
URL_SHORTENERS = {"bit.ly", "tinyurl.com", "cutt.ly", "rb.gy", "is.gd", "t.me", "wa.me"}


def detect_lookalike_domain(domain: str) -> Dict[str, Any]:
    """
    Checks if a domain is a lookalike/typosquat targeting Indian financial or regulatory bodies.
    """
    domain = (domain or "").lower().strip()
    for trusted_dom, name in TRUSTED_FINANCIAL_DOMAINS.items():
        base_keyword = trusted_dom.split(".")[0]
        if base_keyword in domain and domain != trusted_dom and not domain.endswith("." + trusted_dom):
            return {
                "is_lookalike": True,
                "target_entity": f"{name} ({trusted_dom})",
                "trusted_domain": trusted_dom
            }
    major_targets = {
        "sbi": "State Bank of India (sbi.co.in)",
        "hdfc": "HDFC Bank (hdfcbank.com)",
        "icici": "ICICI Bank (icicibank.com)",
        "zerodha": "Zerodha (zerodha.com)",
        "groww": "Groww (groww.in)",
        "nsdl": "NSDL (nsdl.co.in)"
    }
    for kw, label in major_targets.items():
        if kw in domain and not any(trusted in domain for trusted in ["sbi.co.in", "hdfcbank.com", "icicibank.com", "zerodha.com", "groww.in", "nsdl.co.in"]):
            return {
                "is_lookalike": True,
                "target_entity": label,
                "trusted_domain": kw
            }
    return {"is_lookalike": False, "target_entity": None}


def parse_upi_uri(uri: str) -> Dict[str, Any]:
    """
    Parses a UPI payment link (e.g. upi://pay?pa=recipient@upi&pn=RecipientName&am=25000&cu=INR)
    Extracts payee address, payee name, intended amount, and note.
    """
    parsed = urllib.parse.urlparse(uri)
    query_params = urllib.parse.parse_qs(parsed.query)

    pa = query_params.get("pa", [None])[0]
    pn = query_params.get("pn", [None])[0]
    am = query_params.get("am", [None])[0]
    cu = query_params.get("cu", ["INR"])[0]
    tn = query_params.get("tn", [None])[0]

    # Heuristic: Is it likely a personal account (digits or common personal handle)?
    is_personal_handle = False
    if pa:
        prefix = pa.split("@")[0].lower()
        if re.match(r"^\d{10}$", prefix) or any(k in prefix for k in ["user", "pay", "personal", "temp"]):
            is_personal_handle = True

    return {
        "is_upi": True,
        "payee_address": pa,
        "payee_name": pn,
        "amount": am,
        "currency": cu,
        "transaction_note": tn,
        "is_personal_handle": is_personal_handle,
    }


def analyze_url(url: str, claimed_entity: Optional[str] = None) -> Dict[str, Any]:
    """
    Performs forensic inspection on a URL.
    Checks protocol security, domain impersonation, suspicious TLDs, and shorteners.
    """
    url_clean = url.strip().rstrip(".,;)>'\"")
    has_protocol = bool(re.match(r"^https?://", url_clean, re.I))
    full_url = url_clean if has_protocol else f"http://{url_clean}"

    try:
        parsed = urllib.parse.urlparse(full_url)
        domain = parsed.netloc.lower()
        if ":" in domain:
            domain = domain.split(":")[0]
    except Exception:
        domain = url_clean.split("/")[0].lower()

    is_https = parsed.scheme.lower() == "https" if has_protocol else False
    is_shortener = any(domain == s or domain.endswith("." + s) for s in URL_SHORTENERS)

    # Check for suspicious TLD
    has_suspicious_tld = any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS)

    # Typosquatting / Lookalike checks for regulatory bodies
    typosquatting_detected = False
    impersonated_target = None

    for trusted_dom, name in TRUSTED_FINANCIAL_DOMAINS.items():
        base_keyword = trusted_dom.split(".")[0] # e.g. "sebi", "rbi", "bseindia"
        if base_keyword in domain and domain != trusted_dom and not domain.endswith("." + trusted_dom):
            typosquatting_detected = True
            impersonated_target = f"{name} ({trusted_dom})"
            break

    # Claimed entity mismatch
    entity_mismatch = False
    if claimed_entity and len(claimed_entity) >= 4:
        clean_ent = re.sub(r"[^a-z0-9]", "", claimed_entity.lower())
        clean_dom = re.sub(r"[^a-z0-9]", "", domain)
        if clean_ent not in clean_dom and not any(part in clean_dom for part in clean_ent.split()):
            # If domain claims to be different from corporate entity
            entity_mismatch = True

    risk_flags = []
    if not is_https and not domain.endswith(".gov.in"):
        risk_flags.append({
            "code": "INSECURE_HTTP_PROTOCOL",
            "title": "Insecure Link (HTTP)",
            "description": f"URL '{url}' does not use encrypted HTTPS. Official financial institutions universally mandate HTTPS.",
            "severity": "MODERATE"
        })
    if is_shortener:
        risk_flags.append({
            "code": "URL_SHORTENER_DETECTED",
            "title": "Obfuscated / Shortened Link",
            "description": f"URL '{url}' uses a link shortener ({domain}), which obscures the actual destination and is frequently leveraged in malicious financial campaigns.",
            "severity": "HIGH"
        })
    if has_suspicious_tld:
        risk_flags.append({
            "code": "SUSPICIOUS_DOMAIN_TLD",
            "title": "High-Risk Domain Extension",
            "description": f"Domain '{domain}' utilizes an atypical TLD associated with disposable scam websites rather than regulated financial organizations.",
            "severity": "HIGH"
        })
    if typosquatting_detected:
        risk_flags.append({
            "code": "REGULATORY_TYPOSQUATTING",
            "title": f"Lookalike Domain Impersonating {impersonated_target}",
            "description": f"Domain '{domain}' appears engineered to mimic official regulator {impersonated_target}. Regulated entities only operate on their authentic statutory domains.",
            "severity": "CRITICAL"
        })

    return {
        "raw_url": url,
        "clean_url": full_url,
        "domain": domain,
        "is_https": is_https,
        "is_shortener": is_shortener,
        "has_suspicious_tld": has_suspicious_tld,
        "typosquatting_detected": typosquatting_detected,
        "impersonated_target": impersonated_target,
        "entity_mismatch": entity_mismatch,
        "risk_flags": risk_flags,
    }


def detect_and_decode_qrcodes(
    image_input: Any,
    claimed_entity: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Scans the document image for embedded QR codes using OpenCV's multi-detect engine.
    Extracts destination content, computes bounding box coordinates for visual overlay,
    and analyzes payment parameters.
    """
    if isinstance(image_input, Image.Image):
        cv_img = cv2.cvtColor(np.array(image_input.convert("RGB")), cv2.COLOR_RGB2BGR)
    elif isinstance(image_input, str):
        cv_img = cv2.imread(image_input)
    elif isinstance(image_input, np.ndarray):
        cv_img = image_input
    else:
        return []

    if cv_img is None:
        return []

    detector = cv2.QRCodeDetector()
    results = []

    try:
        # Multi-detect QR codes
        ok, decoded_info, points, _ = detector.detectAndDecodeMulti(cv_img)
        if not ok or decoded_info is None or len(decoded_info) == 0:
            # Fallback to single detector
            data, pts, _ = detector.detectAndDecode(cv_img)
            if data and pts is not None:
                decoded_info = [data]
                points = [pts]
            else:
                decoded_info = []

        for i, raw_data in enumerate(decoded_info):
            if not raw_data or not raw_data.strip():
                continue

            qr_text = raw_data.strip()
            bbox = None
            if points is not None and len(points) > i and points[i] is not None:
                pts = points[i].reshape(-1, 2).astype(int)
                x = int(np.min(pts[:, 0]))
                y = int(np.min(pts[:, 1]))
                w = int(np.max(pts[:, 0]) - x)
                h = int(np.max(pts[:, 1]) - y)
                bbox = {"x": max(0, x), "y": max(0, y), "w": max(1, w), "h": max(1, h)}

            # Determine payload type
            is_upi = qr_text.startswith("upi://pay") or "pa=" in qr_text
            upi_details = parse_upi_uri(qr_text) if is_upi else None

            # Determine URL details
            url_analysis = None
            if not is_upi and (qr_text.startswith("http") or "." in qr_text):
                url_analysis = analyze_url(qr_text, claimed_entity=claimed_entity)

            # Build risk assessment for this QR code
            qr_risks = []
            if is_upi:
                if upi_details.get("is_personal_handle"):
                    qr_risks.append({
                        "code": "QR_PERSONAL_UPI_PAYMENT",
                        "title": "QR Directs to Personal / Informal Account",
                        "description": f"QR code encodes a direct transfer to personal handle '{upi_details.get('payee_address')}'. Legitimate corporate investment vehicles accept funds strictly into escrow or corporate clearing accounts, never personal UPI IDs.",
                        "severity": "CRITICAL"
                    })
                else:
                    qr_risks.append({
                        "code": "QR_PAYMENT_COLLECTION",
                        "title": "Embedded Payment QR Code",
                        "description": f"QR code requests payment transfer to '{upi_details.get('payee_address')}'. Users should verify paymentee credentials directly.",
                        "severity": "MODERATE"
                    })
            elif url_analysis:
                qr_risks.extend(url_analysis.get("risk_flags", []))

            results.append({
                "qr_index": i + 1,
                "raw_content": qr_text,
                "bbox": bbox,
                "is_upi": is_upi,
                "upi_details": upi_details,
                "url_analysis": url_analysis,
                "risk_flags": qr_risks,
            })

    except Exception as e:
        # Graceful degradation if QR decoder encounters malformed matrix
        pass

    return results


def extract_and_analyze_urls_from_text(
    text: str,
    claimed_entity: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Discovers all URLs, web domains, and email handles embedded inside document OCR text.
    """
    if not text:
        return []

    url_pattern = r"\b(?:https?://|www\.)[a-zA-Z0-9.\-_~:/?#\[\]@!$&'()*+,;=%]+\b"
    domain_pattern = r"\b[a-zA-Z0-9\-]+\.(?:com|org|in|gov\.in|net|io|xyz|top|cc|online|site|club|co\.in)\b"

    found = set()
    for m in re.finditer(url_pattern, text, re.IGNORECASE):
        found.add(m.group(0))
    for m in re.finditer(domain_pattern, text, re.IGNORECASE):
        dom = m.group(0)
        if not any(dom in u for u in found):
            found.add(dom)

    analyses = []
    for item in sorted(list(found)):
        analyses.append(analyze_url(item, claimed_entity=claimed_entity))

    return analyses
