"""
Proofly Entity & Identity Consistency Engine
Builds an internal identity graph from document text, header entities, email domains,
QR payment recipients, and URLs.
Identifies contradictions between the claimed organization and payment/contact channels.
"""

import re
from typing import List, Dict, Any, Optional

PUBLIC_EMAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com",
    "icloud.com", "protonmail.com", "yandex.com", "mail.com"
}


def build_entity_graph(
    text: str,
    qr_codes: List[Dict[str, Any]],
    urls: List[Dict[str, Any]],
    claimed_entity: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extracts corporate identities, email addresses, phone numbers, and payment endpoints,
    then evaluates their cross-channel consistency.
    """
    if not text:
        return {"entity_map": {}, "mismatches": [], "is_consistent": True}

    # 1. Extract email addresses
    emails = re.findall(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b", text)
    full_emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)

    # 2. Extract phone numbers (Indian 10-digit mobile & landline)
    phones = re.findall(r"(?:\+91[- ]?)?[6-9]\d{9}\b", text)

    # 3. Detect prominent claimed organization
    org_candidate = claimed_entity
    if not org_candidate:
        org_matches = re.findall(
            r"\b(?:[A-Z][a-zA-Z0-9&]+(?:\s+[A-Z][a-zA-Z0-9&]+)*\s+(?:Securities|Capital|Investments|Mutual\s*Fund|Asset\s*Management|Broking|Financial|Advisory|Bank|Wealth|Ventures))\b",
            text
        )
        if org_matches:
            org_candidate = org_matches[0].strip()

    # 4. Extract UPI payment handles from text or QR codes
    upi_payees = []
    seen_pa = set()
    for qr in qr_codes:
        if qr.get("is_upi") and qr.get("upi_details"):
            u = qr["upi_details"]
            pa_addr = u.get("payee_address")
            if pa_addr and pa_addr.lower() not in seen_pa:
                seen_pa.add(pa_addr.lower())
                upi_payees.append({
                    "address": pa_addr,
                    "name": u.get("payee_name"),
                    "source": "QR Code"
                })

    # Standard UPI handles don't have domain dots after @ and aren't webmail providers
    text_upis = re.findall(r"\b[a-zA-Z0-9.\-_]{2,64}@(?!gmail|yahoo|outlook|hotmail|rediff|icloud|proton)[a-zA-Z]{2,32}\b(?!\.[a-zA-Z])", text, re.IGNORECASE)
    for u in text_upis:
        if u.lower() not in seen_pa:
            seen_pa.add(u.lower())
            upi_payees.append({"address": u, "name": None, "source": "Document Text"})

    # Evaluate Inconsistencies
    mismatches = []

    # Inconsistency A: Claimed Corporate Financial Institution using free public webmail
    if org_candidate and full_emails:
        for full_em in full_emails:
            domain = full_em.split("@")[-1].lower()
            if domain in PUBLIC_EMAIL_PROVIDERS:
                mismatches.append({
                    "code": "PUBLIC_EMAIL_FOR_CORPORATE_ENTITY",
                    "title": "Corporate Entity Uses Generic Public Email",
                    "description": (
                        f"Document claims to represent '{org_candidate}', but provides an unofficial public email "
                        f"address '{full_em}'. Regulated financial institutions communicate exclusively through dedicated corporate domains."
                    ),
                    "severity": "CRITICAL",
                    "claimed": org_candidate,
                    "actual": full_em
                })

    # Inconsistency B: Corporate Entity with Personal UPI recipient in QR Code
    if org_candidate and upi_payees:
        for payee in upi_payees:
            pa = payee.get("address", "")
            pn = payee.get("name", "")
            # Check if payee looks like an individual personal name rather than corporate
            clean_org = re.sub(r"[^a-zA-Z0-9]", "", org_candidate.lower())
            clean_pa = re.sub(r"[^a-zA-Z0-9]", "", pa.lower())

            if clean_org not in clean_pa and not any(part in clean_pa for part in clean_org.split()):
                mismatches.append({
                    "code": "UPI_RECIPIENT_IDENTITY_MISMATCH",
                    "title": "Payment Recipient Mismatches Claimed Entity",
                    "description": (
                        f"The document purports to be from '{org_candidate}', but the payment destination ({payee.get('source')}) "
                        f"directs money to '{pa}' ({pn or 'Unspecified Payee'}). Investment funds should never be sent to personal handles."
                    ),
                    "severity": "CRITICAL",
                    "claimed": org_candidate,
                    "actual": f"{pa} ({pn})" if pn else pa
                })

    # Inconsistency C: Website Domain Mismatch
    if org_candidate and urls:
        for u in urls:
            dom = u.get("domain", "")
            clean_org = re.sub(r"[^a-zA-Z0-9]", "", org_candidate.lower())
            clean_dom = re.sub(r"[^a-zA-Z0-9]", "", dom.lower())
            if u.get("typosquatting_detected"):
                mismatches.append({
                    "code": "URL_IDENTITY_TYPOSQUATTING",
                    "title": "Lookalike Domain Linked in Document",
                    "description": f"Linked URL '{dom}' simulates an official regulatory or financial institution domain.",
                    "severity": "CRITICAL",
                    "claimed": org_candidate,
                    "actual": dom
                })

    is_consistent = len(mismatches) == 0

    return {
        "entity_map": {
            "claimed_organization": org_candidate or "Unspecified Entity",
            "emails": list(set(full_emails)),
            "phone_numbers": list(set(phones)),
            "payment_endpoints": upi_payees,
            "associated_domains": [u.get("domain") for u in urls if u.get("domain")]
        },
        "mismatches": mismatches,
        "mismatch_count": len(mismatches),
        "is_consistent": is_consistent
    }
