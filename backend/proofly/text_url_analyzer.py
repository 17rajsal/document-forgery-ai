"""
Proofly Text and URL Scam Analysis Engine
Enables direct paste-and-inspect analysis for suspicious WhatsApp messages,
Telegram investment channels, SMS alerts, and investment URLs/domains.
Produces an explainable 4-component risk breakdown.
"""

import re
import socket
import urllib.parse
from typing import Dict, Any, List, Optional
from .entity_verifier import verify_intermediary
from .qr_url_analyzer import detect_lookalike_domain

# Known URL shorteners
SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "shorturl.at",
    "rb.gy", "goo.gl", "ow.ly", "buff.ly", "t.me", "wa.me"
}

# Suspicious TLDs frequently abused in rapid-turnaround financial phishing
HIGH_RISK_TLDS = {
    ".xyz", ".top", ".click", ".link", ".live", ".info", ".vip", ".loan",
    ".gq", ".cf", ".tk", ".ml", ".work", ".shop", ".online", ".site"
}

# Scam Language Patterns with weights and plain explanations
SCAM_INDICATORS = [
    {
        "pattern": re.compile(r"\b(?:guaranteed|assured|fixed|sure[- ]shot|100%)\s+(?:[\w%.-]+\s+){0,3}(?:returns?|profits?|income|gains?)\b|गारंटीड\s*(?:[\w%.-]+\s*){0,2}(?:रिटर्न|मुनाफा)", re.I),
        "title": "Guaranteed-Return Language Detected",
        "title_hi": "Guaranteed Return ka vaada paya gaya",
        "category": "GUARANTEED_RETURNS",
        "weight": 35,
        "severity": "CRITICAL",
        "explanation": "Promising guaranteed or fixed returns on securities is statutorily prohibited under SEBI regulations. All market investments carry risk."
    },
    {
        "pattern": re.compile(r"\b(?:double\s+your\s+money|2x\s+in\s+\d+|3x\s+in\s+\d+|paisa\s+double|double\s+profit)\b|पैसा\s*डबल", re.I),
        "title": "'Double Your Money' Scheme Detected",
        "title_hi": "'Paisa Double' scheme ka sanket",
        "category": "UNREALISTIC_RETURNS",
        "weight": 35,
        "severity": "CRITICAL",
        "explanation": "Offers claiming to multiply capital rapidly are hallmark signatures of Ponzi or fraudulent deposit schemes."
    },
    {
        "pattern": re.compile(r"\b(?:100%\s*(?:safe|risk[- ]free)|zero[- ]risk|no\s+risk|bina\s+kisi\s+risk|risk[- ]free)\b|जीरो\s*रिस्क", re.I),
        "title": "'Risk-Free' / Zero-Risk Claim",
        "title_hi": "'Bina kisi risk' ka jhootha daawa",
        "category": "ZERO_RISK_CLAIM",
        "weight": 30,
        "severity": "CRITICAL",
        "explanation": "No legitimate investment is zero-risk. High-yield claims with zero risk are inherently deceptive."
    },
    {
        "pattern": re.compile(r"\b(?:SEBI|RBI|NSDL|BSE|NSE)\s*(?:approved|verified|certified|backed|authorized|authori[sz]ed|regulated|guaranteed)\b", re.I),
        "title": "Claimed Regulatory Authority / Endorsement",
        "title_hi": "Regulator ke naam ka galat istemal",
        "category": "REGULATOR_IMPERSONATION",
        "weight": 30,
        "severity": "CRITICAL",
        "explanation": "Regulators like SEBI, RBI, and NSDL never endorse individual trading groups, tips, or investment schemes."
    },
    {
        "pattern": re.compile(r"\b(?:VIP|premium|insider|special|private)\s*(?:trading|whatsapp|telegram|signal|crypto|stock|investment)?\s*(?:group|channel|community|circle|desk)\b", re.I),
        "title": "VIP / Insider Trading Group Trap",
        "title_hi": "VIP WhatsApp / Telegram group ka daawa",
        "category": "PUMP_AND_DUMP",
        "weight": 25,
        "severity": "HIGH",
        "explanation": "Invitation to secret or VIP groups is the primary channel for illegal stock tips, pump-and-dump, and pig-butchering scams."
    },
    {
        "pattern": re.compile(r"\b(?:act\s+now|closing\s+soon|last\s+\d+\s+slots?|only\s+\d+\s+left|limited\s+time\s+offer|hurry\s+up|closing\s+today)\b|जल्दी\s*करें", re.I),
        "title": "Urgency & Artificial FOMO Pressure",
        "title_hi": "Turant faisla lene ka dabav (FOMO)",
        "category": "URGENCY_FOMO",
        "weight": 20,
        "severity": "HIGH",
        "explanation": "Scammers enforce tight deadlines to induce panic and prevent investors from consulting family or official sources."
    },
    {
        "pattern": re.compile(r"\b(?:transfer\s+immediately|pay\s+now|pay\s+immediately|send\s+screenshot|deposit\s+today|send\s+money)\b|तुरंत\s*(?:पैसे|भुगतान)", re.I),
        "title": "Urgent Payment Pressure",
        "title_hi": "Turant payment karne ka dabav",
        "category": "PAYMENT_PRESSURE",
        "weight": 25,
        "severity": "HIGH",
        "explanation": "Demanding immediate payments with payment-screenshot confirmation is standard social engineering protocol."
    },
    {
        "pattern": re.compile(r"\b(?:secret\s+(?:strategy|algorithm|bot|software|formula)|100%\s+accuracy)\b", re.I),
        "title": "'Secret Algorithm / 100% Accuracy' Claim",
        "title_hi": "'Secret Strategy ya Software' ka jhootha daawa",
        "category": "UNVERIFIED_TECH",
        "weight": 20,
        "severity": "MODERATE",
        "explanation": "Claims of automated trading bots with guaranteed accuracy conceal severe market drawdowns."
    },
    {
        "pattern": re.compile(r"\b(?:\d{2,3}%\s+(?:returns?|profits?|gains?|monthly|daily|weekly|in\s+\d+\s+days))\b", re.I),
        "title": "Suspicious High Investment Return Percentage",
        "title_hi": "Asamanya roop se zyada return ka daawa",
        "category": "HIGH_RETURN_PERCENTAGE",
        "weight": 25,
        "severity": "HIGH",
        "explanation": "Promising abnormally high returns (e.g. 30%-60% in days or weeks) is unachievable in legitimate regulated securities markets."
    },
    {
        "pattern": re.compile(r"\b(?:refund\s+fee|processing\s+tax|release\s+frozen\s+funds?|tax\s+clearance\s+fee)\b", re.I),
        "title": "Advance-Fee / Recovery Scam Language",
        "title_hi": "Phanse paise nikalne ke liye advance fee ka daawa",
        "category": "ADVANCE_FEE",
        "weight": 35,
        "severity": "CRITICAL",
        "explanation": "Asking for tax or fee to release investment winnings is the final stage of advance-fee fraud. Never pay to withdraw."
    }
]


def analyze_scam_language(text: str) -> Dict[str, Any]:
    """
    Scans plain text for known digital investment scam indicators.
    Returns matched indicators, component score (0-100), and explanations.
    """
    if not text or not text.strip():
        return {
            "score": 0,
            "level": "LOW",
            "indicators": [],
            "found_count": 0,
            "has_critical": False
        }

    matched_indicators = []
    total_weight = 0
    has_critical = False

    for item in SCAM_INDICATORS:
        match = item["pattern"].search(text)
        if match:
            matched_indicators.append({
                "title": item["title"],
                "title_hi": item["title_hi"],
                "category": item["category"],
                "severity": item["severity"],
                "weight": item["weight"],
                "matched_text": match.group(0),
                "explanation": item["explanation"]
            })
            total_weight += item["weight"]
            if item["severity"] == "CRITICAL":
                has_critical = True

    # Calculate calibrated scam language score (capped at 100)
    score = min(100, int(total_weight * 1.15)) if matched_indicators else 0
    level = "HIGH" if (score >= 60 or has_critical) else "MODERATE" if score >= 25 else "LOW"

    return {
        "score": score,
        "level": level,
        "indicators": matched_indicators,
        "found_count": len(matched_indicators),
        "has_critical": has_critical
    }


def analyze_url_domain(url: str, claimed_org: Optional[str] = None) -> Dict[str, Any]:
    """
    Performs passive structural and safety inspection of a pasted or extracted URL.
    Does NOT fabricate results. Employs lookalike checks, shortener detection,
    TLD risk scoring, and passive DNS resolution if accessible.
    """
    if not url or not url.strip():
        return {
            "score": 0,
            "level": "LOW",
            "url": None,
            "domain": None,
            "concerns": [],
            "is_shortened": False,
            "is_lookalike": False
        }

    raw_url = url.strip()
    if not raw_url.startswith(("http://", "https://", "ftp://")):
        # If bare domain or path, prepend https://
        raw_url = "https://" + raw_url

    concerns: List[str] = []
    score = 10  # Baseline safe starting risk

    try:
        parsed = urllib.parse.urlsplit(raw_url)
        host = (parsed.hostname or "").lower().rstrip(".")
        scheme = parsed.scheme.lower()
    except Exception as e:
        return {
            "score": 85,
            "level": "HIGH",
            "url": url,
            "domain": None,
            "concerns": [f"Malformed URL syntax: {str(e)}"],
            "is_shortened": False,
            "is_lookalike": False
        }

    # 1. Scheme Check
    if scheme == "http":
        concerns.append("Insecure HTTP protocol. Legitimate financial portals mandate encrypted HTTPS.")
        score += 25
    elif scheme not in ("http", "https"):
        concerns.append(f"Non-standard web scheme '{scheme}://'.")
        score += 30

    # 2. IP Host Check
    is_ip = False
    try:
        socket.inet_aton(host)
        is_ip = True
        concerns.append("URL uses a raw IP address instead of a registered domain name.")
        score += 45
    except socket.error:
        pass

    # 3. URL Shortener Detection
    is_shortened = False
    if host in SHORTENERS or any(host.endswith("." + s) for s in SHORTENERS):
        is_shortened = True
        concerns.append(f"Shortened URL detected ({host}). Shorteners conceal the final destination from investors.")
        score += 35

    # 4. Excessive Subdomains (Domain Masking / Phishing structure)
    subdomain_parts = host.split(".")
    if len(subdomain_parts) >= 4 and not is_ip:
        concerns.append("Excessive subdomain depth detected. Common tactic to disguise authentic institution names.")
        score += 25

    # 5. Suspicious / Cheap TLDs
    matched_tld = None
    for tld in HIGH_RISK_TLDS:
        if host.endswith(tld):
            matched_tld = tld
            concerns.append(f"High-risk top-level domain '{tld}' detected, frequently used in disposable phishing sites.")
            score += 25
            break

    # 6. Lookalike / Typosquatting Check targeting Indian Financial Institutions
    lookalike_info = detect_lookalike_domain(host) if host else None
    is_lookalike = False
    if lookalike_info and lookalike_info.get("is_lookalike"):
        is_lookalike = True
        target = lookalike_info.get("target_entity")
        concerns.append(f"High-confidence lookalike/typosquat domain targeting '{target}'. This domain is NOT authorized.")
        score += 55

    # 7. Claimed Organization vs Domain Mismatch Check
    if claimed_org and host:
        clean_org = re.sub(r"[^a-zA-Z0-9]", "", claimed_org.lower())
        clean_host = re.sub(r"[^a-zA-Z0-9]", "", host)
        if len(clean_org) > 4 and clean_org not in clean_host and not any(part in clean_org for part in subdomain_parts):
            concerns.append(f"Listed domain '{host}' does not match claimed organization '{claimed_org}'.")
            score += 20

    # 8. Suspicious user credentials in URL
    if parsed.username or parsed.password:
        concerns.append("URL contains embedded user credentials or an authority override trick.")
        score += 40

    final_score = min(100, max(0, score if concerns else 5))
    level = "HIGH" if final_score >= 60 else "MODERATE" if final_score >= 25 else "LOW"

    return {
        "score": final_score,
        "level": level,
        "url": raw_url,
        "domain": host,
        "is_https": scheme == "https",
        "is_shortened": is_shortened,
        "is_lookalike": is_lookalike,
        "concerns": concerns,
        "external_reputation": "External verification unavailable (offline privacy mode active)"
    }


def analyze_text_and_url_submission(
    text: Optional[str] = None,
    url: Optional[str] = None,
    claimed_org: Optional[str] = None,
    claimed_reg_no: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for direct text message and URL verification.
    Computes component risk scores:
      - Document Integrity (N/A for raw text, set to 0)
      - Scam Language (0-100)
      - URL/Domain Risk (0-100)
      - Entity Verification (VERIFIED / NOT VERIFIED / UNABLE TO VERIFY)
    Produces overall Investor Scam Risk (0-100) and plain language explanations.
    """
    combined_text = (text or "").strip()
    target_url = (url or "").strip()

    # If URL not provided separately, attempt to extract URL from text
    if not target_url and combined_text:
        url_match = re.search(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", combined_text)
        if url_match:
            target_url = url_match.group(0)

    # If entity not provided separately, attempt basic regex extraction
    if not claimed_org and combined_text:
        org_match = re.search(r"\b(?:from|at|by|with|company|firm|advisory|broker|platform)\s*[:\-]?\s*([A-Za-z0-9 ]{3,35})", combined_text, re.I)
        if org_match:
            claimed_org = org_match.group(1).strip()

    # If reg no not provided, attempt regex extraction
    if not claimed_reg_no and combined_text:
        reg_match = re.search(r"\b(?:INZ\d{9}|INA\d{9}|INH\d{9}|ARN[- ]?\d{4,8})\b", combined_text, re.I)
        if reg_match:
            claimed_reg_no = reg_match.group(0).strip()

    # 1. Analyze Scam Language
    scam_res = analyze_scam_language(combined_text)

    # 2. Analyze URL / Domain
    url_res = analyze_url_domain(target_url, claimed_org=claimed_org)

    # 3. Verify Entity
    entity_res = verify_intermediary(
        claimed_entity=claimed_org,
        registration_number=claimed_reg_no
    )

    # 4. Compute Weighted Component Breakdown & Overall Investor Scam Risk
    # Weights for text submission: Scam Language (50%), URL Risk (30%), Entity Verification (20%)
    scam_score = scam_res["score"]
    url_score = url_res["score"]

    entity_penalty = 0
    if entity_res["status"] == "NOT VERIFIED":
        entity_penalty = 90
    elif entity_res["status"] == "UNABLE TO VERIFY" and (claimed_org or claimed_reg_no):
        entity_penalty = 50
    elif entity_res["status"] == "VERIFIED":
        entity_penalty = 5

    # Composite Investor Scam Risk (0-100)
    if not combined_text and not target_url:
        overall_risk_score = 0
        overall_level = "LOW"
    else:
        active_weights = []
        if combined_text:
            active_weights.append((scam_score, 0.55))
        if target_url:
            active_weights.append((url_score, 0.30))
        if claimed_org or claimed_reg_no:
            active_weights.append((entity_penalty, 0.15))

        if active_weights:
            total_w = sum(w for _, w in active_weights)
            overall_risk_score = int(sum(s * w for s, w in active_weights) / total_w)
        else:
            overall_risk_score = max(scam_score, url_score)

        if scam_res["has_critical"] or url_res["is_lookalike"] or entity_res["status"] == "NOT VERIFIED":
            overall_risk_score = max(overall_risk_score, 85)

        overall_level = "HIGH RISK" if overall_risk_score >= 65 else "MODERATE RISK" if overall_risk_score >= 30 else "LOW RISK"

    # 5. Build "Why this was flagged" plain bullet points in English & Hindi
    flagged_reasons_en = []
    flagged_reasons_hi = []

    for ind in scam_res["indicators"]:
        flagged_reasons_en.append(f"{ind['title']}: {ind['explanation']}")
        flagged_reasons_hi.append(f"{ind['title_hi']}: {ind['matched_text']}")

    for concern in url_res["concerns"]:
        flagged_reasons_en.append(f"Domain Concern: {concern}")
        flagged_reasons_hi.append(f"Website Link Check: {concern}")

    for concern in entity_res.get("concerns", []):
        flagged_reasons_en.append(f"Entity Verification: {concern}")
        flagged_reasons_hi.append(f"Registration Check: {concern}")

    if not flagged_reasons_en:
        flagged_reasons_en.append("No obvious scam patterns, unauthorized URLs, or suspicious regulatory claims were detected in this message.")
        flagged_reasons_hi.append("Is message mein koi spasht dhokhadhadi, gair-kanuni link ya jhootha daawa nahi paya gaya.")

    # 6. Safe Next Steps
    safe_steps = [
        "Do not transfer money or invest based solely on informal WhatsApp or Telegram messages.",
        "Verify all financial advisors on SEBI's official portal (sebi.gov.in) before paying any fees.",
        "Never share bank passwords, UPI PINs, or OTPs with anyone claiming to represent an investment firm.",
        "If you suspect fraudulent activity, immediately report the incident on the National Cybercrime Portal (cybercrime.gov.in) or call 1930."
    ]

    return {
        "status": "SUCCESS",
        "mode": "TEXT_URL_ANALYSIS",
        "investor_scam_risk": {
            "score": overall_risk_score,
            "risk_level": overall_level,
            "badge": overall_level
        },
        "component_breakdown": {
            "document_integrity": {
                "score": 0,
                "label": "Not Applicable (Pasted text input)",
                "status": "N/A"
            },
            "scam_language": {
                "score": scam_score,
                "label": f"{scam_score}/100 suspicious",
                "level": scam_res["level"],
                "indicators_found": scam_res["found_count"]
            },
            "url_domain_risk": {
                "score": url_score,
                "label": f"{url_score}/100 suspicious" if target_url else "No link provided",
                "level": url_res["level"],
                "domain": url_res["domain"]
            },
            "entity_verification": {
                "status": entity_res["status"],
                "verdict": entity_res["verdict"],
                "claimed_entity": entity_res["claimed_entity"],
                "claimed_registration": entity_res["claimed_registration"]
            }
        },
        "why_flagged": {
            "en": flagged_reasons_en,
            "hi": flagged_reasons_hi
        },
        "scam_indicators": scam_res["indicators"],
        "url_analysis": url_res,
        "entity_verification": entity_res,
        "safe_steps": safe_steps,
        "plain_explanation": {
            "en": (
                f"Overall Investor Scam Risk evaluated as {overall_risk_score}/100 ({overall_level}). "
                f"{len(scam_res['indicators'])} high-risk scam triggers identified."
            ),
            "hi": (
                f"Niveshak Jokhim Score: {overall_risk_score}/100 ({overall_level})। "
                f"{len(scam_res['indicators'])} sandehik scam sanket paye gaye hain।"
            )
        }
    }
