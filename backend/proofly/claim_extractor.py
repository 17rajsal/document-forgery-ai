"""
Proofly Financial Claim & Scam Language Extractor
Identifies high-risk financial promises, social engineering language,
false regulatory endorsements, artificial urgency, and payment pressure.
Associates each claim with its spatial bounding box and plain-language explanation.
"""

import re
from typing import List, Dict, Any, Optional

CLAIM_PATTERNS = [
    # 1. Guaranteed / Assured Returns (Statutorily prohibited for market investments)
    {
        "category": "GUARANTEED_RETURN_CLAIMS",
        "pattern": r"(?:guaranteed|assured|fixed|100%\s*sure|no\s*loss|risk\s*free|zero\s*risk)\s*(?:return|profit|income|growth|interest|yield|gain|payout)?",
        "severity": "CRITICAL",
        "title": "Unrealistic Guaranteed Return Claim",
        "explanation": "Market-linked investments carry inherent market risks and are statutorily prohibited by SEBI from promising guaranteed or assured returns.",
        "verification_source": "SEBI (Investment Advisers) Regulations & SEBI Investor Portal (investor.sebi.gov.in)"
    },
    {
        "category": "PERFORMANCE_PROMISES",
        "pattern": r"(?:double|triple|2x|3x|5x|10x)\s*(?:your\s*)?(?:money|investment|profit|capital|wealth)|(?:daily|weekly)\s*returns?\s*(?:of\s*)?\d+%",
        "severity": "CRITICAL",
        "title": "Aggressive Capital Multiplication Claim",
        "explanation": "Claims of doubling or tripling capital or daily fixed percentage payouts are hallmarks of Ponzi or fraudulent investment schemes.",
        "verification_source": "RBI Sachet Portal (sachet.rbi.org.in)"
    },

    # 2. Regulatory & Government Impersonation
    {
        "category": "REGULATOR_AUTHORITY_CLAIMS",
        "pattern": r"(?:sebi|rbi|gov(?:ernmen)?t\s*of\s*india|ministry\s*of\s*finance)\s*(?:approved|verified|authorized|endorsed|guaranteed|certified|partnered|backed)",
        "severity": "CRITICAL",
        "title": "Statutory Authority Endorsement Claim",
        "explanation": "SEBI, RBI, and Government of India regulate markets but NEVER endorse, approve, guarantee, or sponsor specific investment opportunities or trading schemes.",
        "verification_source": "SEBI Official Clarification on Unauthorized Claims & Impersonation"
    },
    {
        "category": "REGULATOR_AUTHORITY_CLAIMS",
        "pattern": r"\b(?:sebi\s*registered|rbi\s*approved|sebi\s*license)\b",
        "severity": "MODERATE",
        "title": "Claim of Regulatory Registration",
        "explanation": "While legitimate entities are registered with SEBI, fraudulent actors frequently copy registration numbers of genuine brokers onto fake stationery.",
        "verification_source": "SEBI Recognized Intermediaries Database (sebi.gov.in/sebiweb/other/OtherAction.do?doRecognised=yes)"
    },

    # 3. Urgency & Artificial Scarcity (FOMO)
    {
        "category": "URGENCY_FOMO",
        "pattern": r"(?:act\s*now|last\s*\d+\s*(?:minutes?|hours?)|only\s*\d+\s*(?:slots?|seats?|allocations?)\s*left|limited\s*(?:time\s*)?(?:offer|opportunity|allocation)|exclusive\s*pre-?ipo|closing\s*soon)",
        "severity": "HIGH",
        "title": "Artificial Urgency & Scarcity (FOMO)",
        "explanation": "Scammers use time pressure and simulated scarcity to induce impulsive transfers before the victim can verify authenticity or consult family.",
        "verification_source": "Sangyan Investor Safety Guidelines"
    },

    # 4. Payment Pressure & Direct Transfer
    {
        "category": "PAYMENT_PRESSURE",
        "pattern": r"(?:pay|transfer|deposit|send)\s*(?:immediately|now|urgently|today|within\s*\d+\s*(?:mins?|minutes?|hours?))|(?:qr\s*code\s*below|scan\s*to\s*pay)",
        "severity": "HIGH",
        "title": "Immediate Transfer Request",
        "explanation": "Insistence on immediate direct money transfers via UPI or QR code without an authorized broker portal or application is high-risk.",
        "verification_source": "National Cyber Crime Reporting Portal (cybercrime.gov.in / Dial 1930)"
    },

    # 5. Account Threats & Coercion
    {
        "category": "ACCOUNT_SECURITY_THREATS",
        "pattern": r"(?:account\s*(?:will\s*be\s*)?blocked|legal\s*action|penalty\s*of|forfeiture|funds\s*frozen|kyc\s*suspended)",
        "severity": "CRITICAL",
        "title": "Coercive Account Threat / Intimidation",
        "explanation": "Threatening immediate freezing, penalty, or legal action is a coercive psychological tactic to compel non-deliberative payment.",
        "verification_source": "Ministry of Home Affairs Financial Cyber Fraud Advisory"
    },

    # 6. Pre-IPO & Exclusive Allocation Claims
    {
        "category": "IMPERSONATION_CLAIMS",
        "pattern": r"(?:exclusive\s*pre-?ipo|unlisted\s*shares?\s*guaranteed|institutional\s*quota\s*retail|vip\s*trading\s*group)",
        "severity": "HIGH",
        "title": "Unverified Pre-IPO / VIP Quota Claim",
        "explanation": "Private pre-IPO allocations cannot be lawfully distributed via social media groups, WhatsApp broadcasts, or generic PDFs without formal depository credit.",
        "verification_source": "BSE/NSE Public IPO & Pre-IPO Verification Checklists"
    }
]


def extract_claims_from_text(
    text: str,
    words: List[Dict[str, Any]],
    claimed_entity: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Parses document text for deceptive financial claims, social engineering language,
    and maps them to spatial bounding boxes from OCR coordinates.
    """
    if not text:
        return []

    extracted_claims = []
    seen_spans = set()

    for rule in CLAIM_PATTERNS:
        matches = re.finditer(rule["pattern"], text, re.IGNORECASE)
        for m in matches:
            span = m.span()
            matched_str = m.group(0).strip()

            # Prevent duplicate overlapping captures
            if any(abs(span[0] - s[0]) < 8 for s in seen_spans):
                continue
            seen_spans.add(span)

            # Find matching word bounding boxes
            tokens = matched_str.split()
            first_token = re.sub(r"[^a-zA-Z0-9]", "", tokens[0]).lower() if tokens else ""

            bbox = None
            if first_token:
                for w in words:
                    w_clean = re.sub(r"[^a-zA-Z0-9]", "", w.get("text", "")).lower()
                    if first_token == w_clean or first_token in w_clean:
                        # Estimate phrase bounding box
                        bbox = {
                            "x": w["x"],
                            "y": w["y"],
                            "w": min(int(w["w"] * max(1, len(tokens) * 1.5)), 500),
                            "h": w["h"]
                        }
                        break

            extracted_claims.append({
                "claim_id": f"claim_{len(extracted_claims) + 1}",
                "exact_text": matched_str,
                "category": rule["category"],
                "severity": rule["severity"],
                "title": rule["title"],
                "explanation": rule["explanation"],
                "verification_source": rule["verification_source"],
                "bbox": bbox,
                "associated_entity": claimed_entity or "Unspecified Entity"
            })

    return extracted_claims
