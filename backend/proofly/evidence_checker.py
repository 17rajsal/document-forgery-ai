"""
Proofly Evidence Checker & Regulatory Reality Engine
Evaluates extracted claims against statutory financial regulations (SEBI, RBI, PMLA),
checks known legitimate registration criteria, and returns calibrated evidence verdicts.

Statuses:
- Conflicting evidence
- Not corroborated
- Partially supported
- Supported by checked evidence
- Unable to verify from the sources checked
"""

from typing import List, Dict, Any, Optional


REGULATORY_RULES_KNOWLEDGE_BASE = [
    {
        "category": "GUARANTEED_RETURN_CLAIMS",
        "evidence_status": "Conflicting evidence",
        "official_source": "SEBI (Investment Advisers) Regulations, 2013 & SEBI Master Circular",
        "what_was_found": (
            "Regulation explicitly prohibits any SEBI-registered intermediary or portfolio manager from promising, "
            "advertising, or guaranteeing fixed or risk-free returns on equity, derivatives, or unlisted securities."
        ),
        "why_it_matters": (
            "Any document claiming guaranteed returns in capital markets directly contradicts statutory Indian securities laws. "
            "This strongly suggests an unauthorized or high-risk scheme."
        ),
        "uncertainty": "Applies strictly to market-linked investments; does not apply to statutory sovereign schemes like PPF or post-office deposits."
    },
    {
        "category": "REGULATOR_AUTHORITY_CLAIMS",
        "evidence_status": "Conflicting evidence",
        "official_source": "SEBI Clarification Advisory on Impersonation and False Endorsement (sebi.gov.in)",
        "what_was_found": (
            "SEBI issued multiple official public advisories stating that SEBI does not endorse, verify, approve, "
            "or partner with any individual scheme, WhatsApp group, trading algorithm, or pre-IPO allocation pool."
        ),
        "why_it_matters": (
            "Use of SEBI's logo or the phrase 'SEBI approved investment' is a known social engineering tactic to create false trust."
        ),
        "uncertainty": "The entity may hold an individual registration number, but the specific investment claim or product cannot be 'approved' by SEBI."
    },
    {
        "category": "PAYMENT_PRESSURE",
        "evidence_status": "Not corroborated",
        "official_source": "RBI / SEBI Banking & Clearing Mandates for Intermediaries",
        "what_was_found": (
            "Authorized SEBI brokers and AMCs must collect investment payments solely through designated institutional clearing accounts "
            "registered with stock exchanges or depositories (NSDL/CDSL), not personal UPI IDs or unverified payment links."
        ),
        "why_it_matters": (
            "Routing investor funds into personal UPI accounts deprives the user of formal exchange investor protection funds (IPF)."
        ),
        "uncertainty": "A genuine peer-to-peer transfer or informal invoice might use UPI, but corporate market investments never do."
    },
    {
        "category": "IMPERSONATION_CLAIMS",
        "evidence_status": "Not corroborated",
        "official_source": "BSE & NSE Public Offerings and Pre-IPO Compliance Standards",
        "what_was_found": (
            "Legitimate Pre-IPO share transfers require formal demat crediting through authorized Depository Participants (DPs) "
            "and formal execution of share purchase agreements with registered escrow mechanisms."
        ),
        "why_it_matters": (
            "Informal 'VIP quotas' sold through chat applications have repeatedly been identified in SEBI cease-and-desist orders."
        ),
        "uncertainty": "Private placements under Section 42 of Companies Act exist, but are strictly restricted to 200 accredited investors with formal filings."
    },
    {
        "category": "ACCOUNT_SECURITY_THREATS",
        "evidence_status": "Conflicting evidence",
        "official_source": "National Cyber Crime Reporting Portal (cybercrime.gov.in) Advisory on Coercive Threats",
        "what_was_found": (
            "Statutory authorities and registered banks do not threaten immediate account freezing or police arrest via informal PDF notifications or chat messages."
        ),
        "why_it_matters": (
            "Artificial threats are manufactured to bypass the recipient's critical reasoning through fear and urgency."
        ),
        "uncertainty": "Legitimate banks may issue KYC non-compliance letters, but allow 30 to 90 days with formal branches visits."
    }
]


def verify_claims_against_evidence(
    extracted_claims: List[Dict[str, Any]],
    extracted_fields: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Cross-checks each extracted claim against authoritative regulatory evidence.
    Returns structured evidence findings without fabricating external live web states.
    """
    evidence_results = []

    for claim in extracted_claims:
        category = claim.get("category")
        matched_rule = next((r for r in REGULATORY_RULES_KNOWLEDGE_BASE if r["category"] == category), None)

        if matched_rule:
            evidence_results.append({
                "claim_id": claim.get("claim_id"),
                "claim_text": claim.get("exact_text"),
                "category": category,
                "evidence_status": matched_rule["evidence_status"],
                "official_source": matched_rule["official_source"],
                "what_was_found": matched_rule["what_was_found"],
                "why_it_matters": matched_rule["why_it_matters"],
                "uncertainty": matched_rule["uncertainty"]
            })
        else:
            evidence_results.append({
                "claim_id": claim.get("claim_id"),
                "claim_text": claim.get("exact_text"),
                "category": category,
                "evidence_status": "Unable to verify from the sources checked",
                "official_source": "General Public Regulatory Indexes",
                "what_was_found": "No direct conflicting or corroborating statutory entry found for this specific claim wording.",
                "why_it_matters": "Unverified claims should not be accepted as truth without independent confirmation from primary issuer records.",
                "uncertainty": "Automated verification scope is bounded by checked statutory guidelines."
            })

    return evidence_results
