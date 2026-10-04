"""
Proofly Entity & Registration Verification Layer
Provides structured validation of claimed Indian financial intermediaries (SEBI, NSDL, RBI).
Never fabricates results. Clearly distinguishes VERIFIED, NOT VERIFIED, and UNABLE TO VERIFY.
Uses an offline public directory mirror derived from published SEBI/NSDL registries.
"""

import re
from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher

# Registry Source Attribution
REGISTRY_SOURCE = "SEBI & NSDL Public Directory Reference Mirror (Offline Validated)"

# Public Reference Dataset of Regulated Indian Market Intermediaries
# Source: SEBI & NSDL public directories
PUBLIC_REGISTRY_MIRROR: List[Dict[str, Any]] = [
    {
        "name": "Zerodha Broking Limited",
        "aliases": ["Zerodha", "Zerodha Broking", "Zerodha Capital"],
        "registration_number": "INZ000031633",
        "category": "Stock Broker / Depository Participant",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN300183",
        "official_domain": "zerodha.com",
        "status": "ACTIVE"
    },
    {
        "name": "Nextbillion Technology Private Limited",
        "aliases": ["Groww", "Groww Invest Tech", "Groww Broking"],
        "registration_number": "INZ000301838",
        "category": "Stock Broker / Depository Participant",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN304300",
        "official_domain": "groww.in",
        "status": "ACTIVE"
    },
    {
        "name": "ICICI Securities Limited",
        "aliases": ["ICICI Securities", "ICICIdirect", "I-Sec"],
        "registration_number": "INZ000183631",
        "category": "Stock Broker / Merchant Banker / RA",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN301774",
        "official_domain": "icicisecurities.com",
        "status": "ACTIVE"
    },
    {
        "name": "HDFC Securities Limited",
        "aliases": ["HDFC Securities", "HDFC Sec"],
        "registration_number": "INZ000186937",
        "category": "Stock Broker / Depository Participant",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN300476",
        "official_domain": "hdfcsec.com",
        "status": "ACTIVE"
    },
    {
        "name": "Kotak Securities Limited",
        "aliases": ["Kotak Securities", "Kotak Sec", "Kotak Institutional Equities"],
        "registration_number": "INZ000200137",
        "category": "Stock Broker / Depository Participant",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN300214",
        "official_domain": "kotaksecurities.com",
        "status": "ACTIVE"
    },
    {
        "name": "Angel One Limited",
        "aliases": ["Angel One", "Angel Broking"],
        "registration_number": "INZ000161534",
        "category": "Stock Broker / Depository Participant",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN300757",
        "official_domain": "angelone.in",
        "status": "ACTIVE"
    },
    {
        "name": "5paisa Capital Limited",
        "aliases": ["5paisa", "5paisa Capital"],
        "registration_number": "INZ000010231",
        "category": "Stock Broker / Depository Participant",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN304253",
        "official_domain": "5paisa.com",
        "status": "ACTIVE"
    },
    {
        "name": "RKSV Securities India Private Limited",
        "aliases": ["Upstox", "RKSV Securities"],
        "registration_number": "INZ000185137",
        "category": "Stock Broker / Depository Participant",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN304158",
        "official_domain": "upstox.com",
        "status": "ACTIVE"
    },
    {
        "name": "Motilal Oswal Financial Services Limited",
        "aliases": ["Motilal Oswal", "MOFSL"],
        "registration_number": "INZ000158836",
        "category": "Stock Broker / Depository Participant",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN300484",
        "official_domain": "motilaloswal.com",
        "status": "ACTIVE"
    },
    {
        "name": "Sharekhan Limited",
        "aliases": ["Sharekhan", "Sharekhan BNP Paribas"],
        "registration_number": "INZ000171337",
        "category": "Stock Broker / Depository Participant",
        "regulator": "SEBI",
        "nsdl_dp_id": "IN300513",
        "official_domain": "sharekhan.com",
        "status": "ACTIVE"
    }
]

# Standard Registration Patterns
REG_PATTERNS = {
    "SEBI_BROKER": re.compile(r"^INZ\d{9}$", re.I),
    "SEBI_ADVISER": re.compile(r"^INA\d{9}$", re.I),
    "SEBI_ANALYST": re.compile(r"^INH\d{9}$", re.I),
    "SEBI_PORTFOLIO": re.compile(r"^INP\d{9}$", re.I),
    "NSDL_DP": re.compile(r"^IN\d{6}$", re.I),
    "AMFI_ARN": re.compile(r"^ARN[- ]?\d{4,8}$", re.I)
}


def validate_registration_format(reg_no: str) -> Tuple[bool, str]:
    """
    Checks if a registration string matches standard SEBI / NSDL / AMFI formats.
    Returns (is_valid, category_type).
    """
    if not reg_no:
        return False, "EMPTY"
    clean = re.sub(r"[\s\-_]", "", reg_no.strip().upper())
    for cat, pattern in REG_PATTERNS.items():
        if pattern.match(clean):
            return True, cat
    return False, "INVALID_FORMAT"


def name_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def verify_intermediary(
    claimed_entity: Optional[str] = None,
    registration_number: Optional[str] = None,
    claimed_regulator: Optional[str] = None,
    claimed_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verifies an entity and registration number against the public reference mirror.
    Returns status: VERIFIED | NOT VERIFIED | UNABLE TO VERIFY
    """
    claimed_entity_clean = (claimed_entity or "").strip()
    reg_clean = re.sub(r"[\s\-_]", "", (registration_number or "").strip().upper())

    # Case 1: Neither entity nor registration provided
    if not claimed_entity_clean and not reg_clean:
        return {
            "status": "UNABLE TO VERIFY",
            "verdict": "No organization name or registration number provided for verification.",
            "confidence": 0.0,
            "source": REGISTRY_SOURCE,
            "claimed_entity": None,
            "claimed_registration": None,
            "matched_record": None,
            "concerns": ["Entity name and registration number missing from input."]
        }

    # Format Check for Registration Number if supplied
    has_valid_format = False
    reg_type = "UNKNOWN"
    if reg_clean:
        for p_name, pattern in REG_PATTERNS.items():
            if pattern.match(reg_clean):
                has_valid_format = True
                reg_type = p_name
                break

    # Look for exact registration number match in public directory
    record_by_reg = None
    if reg_clean:
        for r in PUBLIC_REGISTRY_MIRROR:
            if r["registration_number"].upper() == reg_clean or r.get("nsdl_dp_id", "").upper() == reg_clean:
                record_by_reg = r
                break

    # Look for entity name match
    record_by_name = None
    best_ratio = 0.0
    if claimed_entity_clean:
        for r in PUBLIC_REGISTRY_MIRROR:
            r_ratio = name_similarity(claimed_entity_clean, r["name"])
            if r_ratio > best_ratio:
                best_ratio = r_ratio
                record_by_name = r
            for alias in r.get("aliases", []):
                a_ratio = name_similarity(claimed_entity_clean, alias)
                if a_ratio > best_ratio:
                    best_ratio = a_ratio
                    record_by_name = r

        if best_ratio < 0.65:
            record_by_name = None

    # SCENARIO A: Registration number provided but matches a DIFFERENT organization
    if record_by_reg and claimed_entity_clean:
        # Check if claimed name matches the registration record
        matches_owner = False
        if name_similarity(claimed_entity_clean, record_by_reg["name"]) > 0.6:
            matches_owner = True
        for alias in record_by_reg.get("aliases", []):
            if name_similarity(claimed_entity_clean, alias) > 0.6:
                matches_owner = True

        if not matches_owner:
            return {
                "status": "NOT VERIFIED",
                "verdict": (
                    f"CRITICAL: Claimed registration number '{registration_number}' belongs to "
                    f"'{record_by_reg['name']}', not '{claimed_entity_clean}'. Potential impersonation / spoofing."
                ),
                "confidence": 0.95,
                "source": REGISTRY_SOURCE,
                "claimed_entity": claimed_entity_clean,
                "claimed_registration": registration_number,
                "matched_record": {
                    "official_name": record_by_reg["name"],
                    "category": record_by_reg["category"],
                    "official_domain": record_by_reg["official_domain"]
                },
                "concerns": [
                    f"Registration number belongs to {record_by_reg['name']}, not the claimed sender {claimed_entity_clean}.",
                    "Impersonation of regulated intermediaries is a common hallmark of digital investment fraud."
                ]
            }

    # SCENARIO B: Both registration number and entity match an active entry
    if record_by_reg and (not claimed_entity_clean or record_by_reg == record_by_name):
        return {
            "status": "VERIFIED",
            "verdict": (
                f"VERIFIED: '{record_by_reg['name']}' is a recognized {record_by_reg['category']} "
                f"registered with {record_by_reg['regulator']} under {record_by_reg['registration_number']}."
            ),
            "confidence": 0.95,
            "source": REGISTRY_SOURCE,
            "claimed_entity": claimed_entity_clean,
            "claimed_registration": registration_number,
            "matched_record": {
                "official_name": record_by_reg["name"],
                "category": record_by_reg["category"],
                "registration_number": record_by_reg["registration_number"],
                "regulator": record_by_reg["regulator"],
                "official_domain": record_by_reg["official_domain"],
                "nsdl_dp_id": record_by_reg.get("nsdl_dp_id")
            },
            "concerns": []
        }

    # SCENARIO C: Registration number provided has completely invalid format
    if reg_clean and not has_valid_format:
        return {
            "status": "NOT VERIFIED",
            "verdict": (
                f"Registration number '{registration_number}' does not follow standard regulatory format. "
                "SEBI broker registrations begin with 'INZ', advisers with 'INA', analysts with 'INH'."
            ),
            "confidence": 0.90,
            "source": REGISTRY_SOURCE,
            "claimed_entity": claimed_entity_clean,
            "claimed_registration": registration_number,
            "matched_record": None,
            "concerns": [
                f"Invalid regulatory identifier format: '{registration_number}'.",
                "Legitimate market entities hold standard 12-character SEBI registration numbers."
            ]
        }

    # SCENARIO D: Entity name recognized, but no registration number or unverified registration
    if record_by_name and not reg_clean:
        return {
            "status": "VERIFIED",
            "verdict": (
                f"Organization '{record_by_name['name']}' is recognized as an active registered intermediary "
                f"({record_by_name['category']}). Verify the contact domain matches {record_by_name['official_domain']}."
            ),
            "confidence": 0.85,
            "source": REGISTRY_SOURCE,
            "claimed_entity": claimed_entity_clean,
            "claimed_registration": None,
            "matched_record": {
                "official_name": record_by_name["name"],
                "category": record_by_name["category"],
                "official_registration": record_by_name["registration_number"],
                "official_domain": record_by_name["official_domain"]
            },
            "concerns": [
                "Document does not state registration number for direct verification."
            ]
        }

    # SCENARIO E: Registration number or entity could not be verified in offline mirror
    concerns = []
    if reg_clean:
        concerns.append(f"Registration number '{registration_number}' was not found in the public reference mirror.")
    if claimed_entity_clean:
        concerns.append(f"Entity '{claimed_entity_clean}' is not listed in the public reference mirror.")

    return {
        "status": "UNABLE TO VERIFY",
        "verdict": (
            "Registration status could not be independently corroborated against the local public directory mirror. "
            "Please check SEBI's official live directory at sebi.gov.in."
        ),
        "confidence": 0.40,
        "source": REGISTRY_SOURCE,
        "claimed_entity": claimed_entity_clean or None,
        "claimed_registration": registration_number or None,
        "matched_record": None,
        "concerns": concerns
    }
