import re


def normalize_text(text):
    """
    Normalize OCR text for document classification.
    """

    if not text:
        return ""

    text = text.lower()

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def has_any(text, keywords):
    """
    Check whether any keyword exists in OCR text.
    """

    return any(
        keyword.lower() in text
        for keyword in keywords
    )


def classify_document(text):
    """
    Identify the likely document type from OCR text.

    Classification is based on multiple keywords rather than
    requiring every field to be present.
    """

    text = normalize_text(text)

    if not text:
        return "Unknown"


    # =====================================================
    # AADHAAR / GOVERNMENT ID
    # =====================================================

    aadhaar_keywords = [
        "government of india",
        "uidai",
        "aadhaar",
        "unique identification",
        "unique identification authority",
        "dob",
        "date of birth",
        "male",
        "female"
    ]

    aadhaar_score = sum(
        1 for keyword in aadhaar_keywords
        if keyword in text
    )

    # Government of India + DOB is a strong signal
    if (
        aadhaar_score >= 2
        or (
            "government of india" in text
            and (
                "dob" in text
                or "date of birth" in text
            )
        )
    ):
        return "Aadhaar / Government ID"


    # =====================================================
    # COLLEGE / STUDENT ID
    # =====================================================

    college_keywords = [
        "identity card",
        "student id",
        "student identity",
        "enrollment no",
        "enrollment number",
        "enrolment no",
        "enrolment number",
        "class roll no",
        "roll no",
        "father's name",
        "father name",
        "blood group",
        "course",
        "institute of technology",
        "college",
        "university"
    ]

    college_score = sum(
        1 for keyword in college_keywords
        if keyword in text
    )

    if college_score >= 2:
        return "College / Student ID"


    # =====================================================
    # BANK MANDATE
    # =====================================================

    bank_mandate_keywords = [
        "electronic clearing service",
        "credit clearing",
        "model mandate form",
        "investor/customer",
        "investor customer",
        "name of the bank",
        "name of the branch",
        "micr",
        "ledger",
        "account number",
        "bank's stamp",
        "authorised official of the bank",
        "authorized official of the bank"
    ]

    bank_score = sum(
        1 for keyword in bank_mandate_keywords
        if keyword in text
    )

    if bank_score >= 2:
        return "Bank Mandate"


    # =====================================================
    # MARKSHEET / EDUCATIONAL CERTIFICATE
    # =====================================================

    marksheet_keywords = [
        "central board of secondary education",
        "marks statement",
        "marks statement cum certificate",
        "secondary school examination",
        "scholastic achievements",
        "subject",
        "theory",
        "total in words",
        "grade",
        "result",
        "pass",
        "controller of examinations"
    ]

    marksheet_score = sum(
        1 for keyword in marksheet_keywords
        if keyword in text
    )

    if marksheet_score >= 2:
        return "Marksheet / Academic Certificate"


    # =====================================================
    # GENERIC BANK DOCUMENT
    # =====================================================

    bank_keywords = [
        "bank",
        "account number",
        "ifsc",
        "micr",
        "branch",
        "customer"
    ]

    bank_score = sum(
        1 for keyword in bank_keywords
        if keyword in text
    )

    if bank_score >= 2:
        return "Bank Document"


    # =====================================================
    # GENERIC CERTIFICATE
    # =====================================================

    certificate_keywords = [
        "certificate",
        "certify that",
        "this is to certify",
        "issued to",
        "date of issue",
        "signature of"
    ]

    certificate_score = sum(
        1 for keyword in certificate_keywords
        if keyword in text
    )

    if certificate_score >= 2:
        return "Certificate"


    # =====================================================
    # INVOICE / FINANCIAL RECEIPT
    # =====================================================

    invoice_keywords = [
        "tax invoice",
        "invoice",
        "bill to",
        "ship to",
        "invoice no",
        "invoice date",
        "subtotal",
        "total amount",
        "grand total",
        "balance due",
        "amount paid",
        "gstin",
        "hsn",
        "receipt",
        "payment receipt",
        "unit price",
        "qty"
    ]

    invoice_score = sum(
        1 for keyword in invoice_keywords
        if keyword in text
    )

    if invoice_score >= 2 or (("invoice" in text or "receipt" in text) and ("total" in text or "amount" in text or "gstin" in text)):
        return "Invoice / Financial Receipt"


    # =====================================================
    # GENERAL SCANNED / UNKNOWN
    # =====================================================

    return "General Document"


DOCUMENT_CATEGORIES = [
    "id_card",
    "certificate",
    "marksheet",
    "invoice_receipt",
    "general_scanned",
]

CATEGORY_DISPLAY_NAMES = {
    "id_card": "ID / Document Card",
    "certificate": "Certificate",
    "marksheet": "Marksheet",
    "invoice_receipt": "Invoice / Receipt",
    "general_scanned": "General Scanned Document",
}


def get_standard_category(document_type_or_text: str) -> str:
    """
    Normalizes any document classification label or raw OCR text into
    one of the 5 standardized forensic categories:
      - id_card
      - certificate
      - marksheet
      - invoice_receipt
      - general_scanned
    """
    if not document_type_or_text:
        return "general_scanned"

    s = document_type_or_text.strip().lower()

    if s in DOCUMENT_CATEGORIES:
        return s

    if any(k in s for k in ["id", "aadhaar", "student", "identity card", "passport", "license", "voter"]):
        return "id_card"
    elif any(k in s for k in ["marksheet", "marks statement", "grade", "cbse", "transcript"]):
        return "marksheet"
    elif any(k in s for k in ["invoice", "receipt", "bill", "tax invoice", "subtotal", "gstin"]):
        return "invoice_receipt"
    elif any(k in s for k in ["certificate", "certify", "completion", "degree", "diploma"]):
        return "certificate"
    elif any(k in s for k in ["bank", "mandate", "statement", "general", "scanned", "contract", "letter", "unknown"]):
        return "general_scanned"

    # Try classifying raw text if input was not already a label
    classified = classify_document(document_type_or_text)
    if classified != "General Document":
        return get_standard_category(classified)

    return "general_scanned"
