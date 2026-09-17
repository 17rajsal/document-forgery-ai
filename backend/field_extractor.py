import re


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_value(value):
    """
    Clean OCR output before returning it.
    """

    if not value:
        return None

    value = value.strip()

    # Remove common OCR punctuation
    value = value.strip(" :,-|.")

    # Remove repeated spaces
    value = re.sub(r"\s+", " ", value)

    if len(value) < 2:
        return None

    return value


def unique_list(items):
    """
    Remove duplicates while preserving order.
    """

    result = []

    for item in items:

        item = clean_value(item)

        if item and item not in result:
            result.append(item)

    return result


# =========================================================
# GENERIC FIELD EXTRACTION
# =========================================================

def extract_generic_fields(text):
    """
    Extract common fields from any document.

    Documents do NOT need to contain all fields.
    Missing fields are returned as empty lists or None.
    """

    result = {
        "dates": [],
        "numbers": [],
        "names": [],
        "account_number": None,
        "bank_name": None,
        "branch_name": None,
        "phone_number": None
    }

    if not text:
        return result

    # =====================================================
    # DATE EXTRACTION
    # =====================================================

    date_patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2}\b",
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"
    ]

    dates = []

    for pattern in date_patterns:

        matches = re.findall(
            pattern,
            text
        )

        dates.extend(matches)

    result["dates"] = unique_list(dates)

    # =====================================================
    # LONG / IMPORTANT NUMBERS
    # =====================================================

    number_patterns = [
        r"\b\d{10,18}\b",
        r"\b\d{6,9}\b"
    ]

    numbers = []

    for pattern in number_patterns:

        matches = re.findall(
            pattern,
            text
        )

        numbers.extend(matches)

    result["numbers"] = unique_list(numbers)

    # =====================================================
    # ACCOUNT NUMBER
    # =====================================================

    account_patterns = [
        r"(?:account\s*(?:number|no\.?|#))\s*[:\-]?\s*([0-9]{6,18})",

        r"(?:a/c|a\.c\.|ac)\s*"
        r"(?:number|no\.?|#)?\s*[:\-]?\s*"
        r"([0-9]{6,18})"
    ]

    for pattern in account_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            result["account_number"] = clean_value(
                match.group(1)
            )

            break

    # =====================================================
    # BANK NAME
    # =====================================================

    bank_patterns = [
        r"name\s+of\s+the\s+bank\s*[:\-]?\s*(.+)",
        r"bank\s*name\s*[:\-]?\s*(.+)",
        r"bank\s*[:\-]\s*(.+)"
    ]

    for pattern in bank_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = clean_value(
                match.group(1)
            )

            if value:

                value = value.split("\n")[0]

                result["bank_name"] = value

                break

    # =====================================================
    # BRANCH NAME
    # =====================================================

    branch_patterns = [
        r"name\s+of\s+the\s+branch\s*[:\-]?\s*(.+)",
        r"branch\s*name\s*[:\-]?\s*(.+)",
        r"branch\s*[:\-]\s*(.+)"
    ]

    for pattern in branch_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = clean_value(
                match.group(1)
            )

            if value:

                value = value.split("\n")[0]

                result["branch_name"] = value

                break

    # =====================================================
    # PHONE NUMBER
    # =====================================================

    phone_patterns = [
        r"\b[6-9]\d{9}\b",
        r"\b0\d{2,4}[- ]?\d{6,8}\b"
    ]

    phones = []

    for pattern in phone_patterns:

        matches = re.findall(
            pattern,
            text
        )

        phones.extend(matches)

    phones = unique_list(phones)

    if phones:

        result["phone_number"] = phones[0]

    # =====================================================
    # GENERIC NAME EXTRACTION
    # =====================================================

    name_patterns = [

        # Name: RAJ SALONIA
        r"(?:name|NAME)\s*[:\-]\s*"
        r"([A-Za-z][A-Za-z .]{2,60})",

        # Applicant Name: RAJ SALONIA
        r"(?:applicant|customer|investor|student)\s*"
        r"(?:name)?\s*[:\-]\s*"
        r"([A-Za-z][A-Za-z .]{2,60})",

        # S/O: GHANSHYAM
        r"(?:S/O|D/O|W/O)\s*[:\-]?\s*"
        r"([A-Za-z][A-Za-z .]{2,60})"
    ]

    names = []

    for pattern in name_patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for name in matches:

            name = clean_value(name)

            if name:

                # Prevent huge OCR lines
                # from being considered names.
                if len(name.split()) <= 6:

                    names.append(name)

    result["names"] = unique_list(names)

    return result


# =========================================================
# COLLEGE / STUDENT ID EXTRACTION
# =========================================================

def extract_college_id_fields(text, words=None):
    """
    Extract college/student ID fields.

    If OCR word-position data is supplied, labels are used to find
    nearby values. This is more reliable than searching the whole OCR
    text because the same number/name may appear several times.
    """

    result = {
        "dates": [],
        "numbers": [],
        "names": [],
        "enrollment_number": None,
        "roll_number": None,
        "father_name": None,
        "mother_name": None,
        "address": None,
        "blood_group": None
    }

    if not text:
        return result

    # Dates
    dates = []
    for pattern in [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"
    ]:
        dates.extend(re.findall(pattern, text))
    result["dates"] = unique_list(dates)

    # Numbers
    result["numbers"] = unique_list(
        re.findall(r"\b\d{5,18}\b", text)
    )

    # -----------------------------------------------------
    # Coordinate-based extraction
    # -----------------------------------------------------

    if words:

        normalized = []

        for word in words:
            value = str(word.get("text", "")).strip()

            if value:
                normalized.append({
                    **word,
                    "text": value,
                    "lower": value.lower()
                })

        def nearby_value(labels, max_x_distance=450, max_y_distance=35):
            """
            Find OCR words immediately to the right of a label.
            """

            labels = [x.lower() for x in labels]

            for i, word in enumerate(normalized):

                current = word["lower"]

                # Normal one-word label
                matched = any(label in current for label in labels)

                # OCR may split a label into multiple words
                if not matched:
                    combined = " ".join(
                        x["lower"]
                        for x in normalized[i:i + 3]
                    )

                    matched = any(
                        label in combined
                        for label in labels
                    )

                if not matched:
                    continue

                label_right = word["x"] + word["w"]
                label_y = word["y"]

                candidates = []

                for candidate in normalized:

                    if candidate["x"] < label_right:
                        continue

                    if abs(candidate["y"] - label_y) > max_y_distance:
                        continue

                    distance = candidate["x"] - label_right

                    if distance <= max_x_distance:
                        candidates.append(candidate)

                candidates.sort(key=lambda x: x["x"])

                if candidates:
                    return " ".join(
                        x["text"] for x in candidates[:6]
                    )

            return None

        # Enrollment
        value = nearby_value(["enrollment", "enrolment"])

        if value:
            value = re.sub(r"[^A-Za-z0-9]", "", value)

            if len(value) >= 5:
                result["enrollment_number"] = value

        # Father
        value = nearby_value(["father", "fathers"])

        if value:
            value = clean_value(value)

            if value:
                result["father_name"] = value

        # Mother
        value = nearby_value(["mother", "mothers"])

        if value:
            value = clean_value(value)

            if value:
                result["mother_name"] = value

        # Address
        value = nearby_value(["address", "adddress"])

        if value:
            value = clean_value(value)

            if value:
                result["address"] = value

        # Blood group
        value = nearby_value(["blood"])

        if value:
            match = re.search(
                r"\b(AB|A|B|O)\s*([+-])\b",
                value,
                re.IGNORECASE
            )

            if not match:
                match = re.search(
                    r"\b(AB|A|B|O)([+-])\b",
                    value,
                    re.IGNORECASE
                )

            if match:
                result["blood_group"] = (
                    match.group(1).upper() +
                    match.group(2)
                )

        # Roll number
        value = nearby_value([
            "class roll",
            "roll no",
            "roll"
        ])

        if value:
            match = re.search(r"\b\d{1,15}\b", value)

            if match:
                result["roll_number"] = match.group(0)

        # Student name
        value = nearby_value([
            "student name",
            "name"
        ])

        if value:
            value = clean_value(value)

            if value and len(value.split()) <= 5:
                result["names"] = [value]

    # -----------------------------------------------------
    # Fallback regex extraction
    # -----------------------------------------------------

    if not result["enrollment_number"]:

        for pattern in [
            r"enrollment\s*(?:no\.?|number)?\s*[:\-]?\s*([A-Za-z0-9./-]{5,25})",
            r"enrolment\s*(?:no\.?|number)?\s*[:\-]?\s*([A-Za-z0-9./-]{5,25})"
        ]:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                value = re.sub(
                    r"[^A-Za-z0-9]",
                    "",
                    match.group(1)
                )

                if len(value) >= 5:
                    result["enrollment_number"] = value

                break

    if not result["roll_number"]:

        for pattern in [
            r"class\s*roll\s*(?:no\.?|number)?\s*[:\-]?\s*(\d{1,15})",
            r"roll\s*(?:no\.?|number)?\s*[:\-]?\s*(\d{1,15})"
        ]:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                result["roll_number"] = match.group(1)
                break

    if not result["father_name"]:

        match = re.search(
            r"father'?s?\s*(?:name)?\s*[:\-]?\s*([A-Za-z][A-Za-z .]{2,60})",
            text,
            re.IGNORECASE
        )

        if match:
            result["father_name"] = clean_value(match.group(1))

    if not result["mother_name"]:

        match = re.search(
            r"mother'?s?\s*(?:name)?\s*[:\-]?\s*([A-Za-z][A-Za-z .]{2,60})",
            text,
            re.IGNORECASE
        )

        if match:
            result["mother_name"] = clean_value(match.group(1))

    if not result["blood_group"]:

        match = re.search(
            r"\b(AB|A|B|O)\s*([+-])\b",
            text,
            re.IGNORECASE
        )

        if match:
            result["blood_group"] = (
                match.group(1).upper() + match.group(2)
            )

    if not result["address"]:

        match = re.search(
            r"address\s*[:\-]\s*(.+)",
            text,
            re.IGNORECASE
        )

        if match:
            result["address"] = clean_value(
                match.group(1).split("\n")[0]
            )

    if not result["names"]:

        names = []

        for pattern in [
            r"(?:student\s*)?name\s*[:\-]?\s*([A-Za-z][A-Za-z .]{2,60})",
            r"this\s+is\s+to\s+certify\s+that\s+([A-Za-z][A-Za-z .]{2,60})"
        ]:

            for name in re.findall(
                pattern,
                text,
                re.IGNORECASE
            ):

                name = clean_value(name)

                if name and len(name.split()) <= 5:
                    names.append(name)

        result["names"] = unique_list(names)


    return result

# =========================================================
# ALGORITHMIC VALIDATION HELPERS
# =========================================================

VERHOEFF_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
)

VERHOEFF_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8)
)


def validate_verhoeff(num_str):
    """
    Validates a 12-digit number using the official Verhoeff checksum algorithm.
    """
    if not num_str:
        return False
    clean_num = re.sub(r"\D", "", str(num_str))
    if len(clean_num) != 12:
        return False
    c = 0
    for i, digit in enumerate(reversed(clean_num)):
        c = VERHOEFF_D[c][VERHOEFF_P[i % 8][int(digit)]]
    return c == 0


def validate_pan(pan_str):
    """
    Validates Indian Permanent Account Number (PAN) structure.
    Format: 5 uppercase letters + 4 digits + 1 uppercase letter.
    """
    if not pan_str:
        return False
    clean = pan_str.strip().upper()
    return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", clean))


def validate_ifsc(ifsc_str):
    """
    Validates Indian Financial System Code (IFSC) format.
    Format: 4 letters + '0' + 6 alphanumeric characters.
    """
    if not ifsc_str:
        return False
    clean = re.sub(r"\s+", "", str(ifsc_str)).upper()
    return bool(re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", clean))


def validate_date_sanity(date_str):
    """
    Validates basic plausibility of a date string (e.g. DD/MM/YYYY).
    """
    if not date_str:
        return True, "No date to check"
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", date_str)
    if not m:
        return True, "Valid or unformatted"
    day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if month < 1 or month > 12 or day < 1 or day > 31:
        return False, f"Invalid calendar date: {date_str}"
    if year < 1920 or year > 2030:
        return False, f"Suspicious out-of-range year ({year})"
    return True, "Valid date"


def extract_aadhaar_fields(text):
    """
    Extract fields commonly found in Aadhaar / Government ID documents
    and execute Verhoeff checksum validation.
    """
    result = {
        "dates": [],
        "numbers": [],
        "names": [],
        "date_of_birth": None,
        "aadhaar_number": None,
        "gender": None,
        "address": None,
        "validations": []
    }

    if not text:
        return result

    # -----------------------------------------------------
    # DATE EXTRACTION
    # -----------------------------------------------------
    date_patterns = [
        r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
        r"\b\d{2}[/-]\d{2}[/-]\d{2}\b"
    ]

    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for value in matches:
            if value not in dates:
                dates.append(value)
    result["dates"] = dates

    # -----------------------------------------------------
    # DATE OF BIRTH
    # -----------------------------------------------------
    dob_patterns = [
        r"(?:DOB|D\.O\.B|Date of Birth|Birth)\s*[:\-]?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
        r"(?:DOB|D\.O\.B|Date of Birth|Birth)\s*[:\-]?\s*(\d{2}[/-]\d{2}[/-]\d{2})"
    ]

    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            dob_val = match.group(1)
            result["date_of_birth"] = dob_val
            is_valid_date, reason = validate_date_sanity(dob_val)
            if not is_valid_date:
                result["validations"].append({
                    "code": "INVALID_DOB_FORMAT",
                    "title": "Invalid Date of Birth Found",
                    "description": reason,
                    "severity": "WARNING",
                    "weight": 15
                })
            break

    # -----------------------------------------------------
    # AADHAAR NUMBER & VERHOEFF CHECKSUM
    # -----------------------------------------------------
    aadhaar_patterns = [
        r"\b\d{4}\s\d{4}\s\d{4}\b",
        r"\b\d{12}\b"
    ]

    for pattern in aadhaar_patterns:
        match = re.search(pattern, text)
        if match:
            raw_aadhaar = match.group(0)
            clean_aadhaar = re.sub(r"\s+", "", raw_aadhaar)
            result["aadhaar_number"] = raw_aadhaar

            # Run official Verhoeff checksum algorithm
            if validate_verhoeff(clean_aadhaar):
                result["validations"].append({
                    "code": "VALID_AADHAAR_CHECKSUM",
                    "title": "Aadhaar Verhoeff Checksum Valid",
                    "description": f"Aadhaar number {raw_aadhaar} satisfies the mathematical Verhoeff checksum digit.",
                    "severity": "VERIFIED",
                    "weight": 0
                })
            else:
                result["validations"].append({
                    "code": "INVALID_AADHAAR_CHECKSUM",
                    "title": "Aadhaar Checksum Failure (Fabricated ID Number)",
                    "description": f"The 12-digit Aadhaar number '{raw_aadhaar}' failed the official Verhoeff checksum algorithm. This strongly indicates a randomly generated or manipulated ID.",
                    "severity": "CRITICAL",
                    "weight": 35
                })
            break

    # -----------------------------------------------------
    # NUMBERS
    # -----------------------------------------------------
    numbers = re.findall(r"\b\d{4,16}\b", text)
    result["numbers"] = list(dict.fromkeys(numbers))

    # -----------------------------------------------------
    # GENDER
    # -----------------------------------------------------
    gender_patterns = [r"\bMALE\b", r"\bFEMALE\b", r"\bTRANSGENDER\b"]
    for gender in gender_patterns:
        if re.search(gender, text, re.IGNORECASE):
            result["gender"] = gender.title()
            break

    # -----------------------------------------------------
    # NAME
    # -----------------------------------------------------
    name_patterns = [
        r"(?:Name|NAME)\s*[:\-]?\s*([A-Za-z ]{3,50})",
        r"(?:S/O|D/O|W/O)\s*[:\-]?\s*([A-Za-z ]{3,50})"
    ]
    names = []
    for pattern in name_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for name in matches:
            name = name.strip()
            if name and name not in names and len(name.split()) <= 5:
                names.append(name)
    result["names"] = names

    # -----------------------------------------------------
    # ADDRESS
    # -----------------------------------------------------
    address_match = re.search(
        r"(?:Address|ADDRESS)\s*[:\-]?\s*(.{10,200})",
        text,
        re.IGNORECASE
    )
    if address_match:
        result["address"] = address_match.group(1).strip()

    return result


def extract_marksheet_fields(text):
    """
    Extract fields specific to academic marksheets, diplomas, and grade cards.
    """
    result = {
        "dates": [],
        "numbers": [],
        "names": [],
        "roll_number": None,
        "registration_number": None,
        "board_university": None,
        "result_status": None,
        "total_marks": None,
        "validations": []
    }

    if not text:
        return result

    # Board / University
    board_match = re.search(
        r"(cbse|central board of secondary education|council for the indian school certificate|icse|up board|university of [A-Za-z ]+|board of technical education)",
        text,
        re.IGNORECASE
    )
    if board_match:
        result["board_university"] = board_match.group(0).strip().title()

    # Roll Number
    roll_match = re.search(
        r"(?:roll\s*(?:no\.?|number)?)\s*[:\-]?\s*([A-Za-z0-9]{4,15})",
        text,
        re.IGNORECASE
    )
    if roll_match:
        result["roll_number"] = roll_match.group(1).strip()

    # Result / Division
    res_match = re.search(
        r"\b(PASS|PASSED|FIRST DIVISION|SECOND DIVISION|DISTINCTION|FAILED|COMPARTMENT)\b",
        text,
        re.IGNORECASE
    )
    if res_match:
        result["result_status"] = res_match.group(0).upper()

    # Generic numbers and dates
    result["numbers"] = unique_list(re.findall(r"\b\d{5,16}\b", text))
    result["dates"] = unique_list(re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text))

    return result


def extract_bank_fields(text):
    """
    Extract fields specific to bank statements, mandates, and cheques.
    """
    result = {
        "dates": [],
        "numbers": [],
        "names": [],
        "account_number": None,
        "bank_name": None,
        "branch_name": None,
        "ifsc_code": None,
        "micr_code": None,
        "validations": []
    }

    if not text:
        return result

    # Generic extraction base
    generic = extract_generic_fields(text)
    result["account_number"] = generic.get("account_number")
    result["bank_name"] = generic.get("bank_name")
    result["branch_name"] = generic.get("branch_name")
    result["dates"] = generic.get("dates", [])
    result["numbers"] = generic.get("numbers", [])
    result["names"] = generic.get("names", [])

    # IFSC Code
    ifsc_match = re.search(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", text)
    if ifsc_match:
        result["ifsc_code"] = ifsc_match.group(0)
        result["validations"].append({
            "code": "VALID_IFSC_FORMAT",
            "title": "Valid IFSC Code Format",
            "description": f"IFSC code '{result['ifsc_code']}' follows standard RBI structure.",
            "severity": "VERIFIED",
            "weight": 0
        })

    # MICR Code (9 digits)
    micr_match = re.search(r"(?:micr|micr code)\s*[:\-]?\s*(\d{9})\b", text, re.IGNORECASE)
    if micr_match:
        result["micr_code"] = micr_match.group(1)

    return result


def extract_invoice_fields(text):
    """
    Extract fields specific to commercial invoices, tax receipts, and bills.
    """
    result = {
        "dates": [],
        "numbers": [],
        "names": [],
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "total_amount": None,
        "tax_amount": None,
        "vendor_name": None,
        "gstin": None,
        "validations": []
    }

    if not text:
        return result

    # Generic base
    generic = extract_generic_fields(text)
    result["dates"] = generic.get("dates", [])
    result["numbers"] = generic.get("numbers", [])
    result["names"] = generic.get("names", [])

    # Invoice Number
    inv_match = re.search(r"(?:invoice\s*(?:no\.?|number|#)?)\s*[:\-]?\s*([A-Za-z0-9\-_/]{3,25})", text, re.IGNORECASE)
    if inv_match:
        result["invoice_number"] = inv_match.group(1).strip()

    # Total Amount
    amt_match = re.search(r"(?:total\s*(?:amount)?|grand\s*total|balance\s*due|amount\s*payable)\s*[:\-]?\s*(?:[$₹€£]|rs\.?|inr)?\s*([\d,]+\.?\d{0,2})", text, re.IGNORECASE)
    if amt_match:
        result["total_amount"] = amt_match.group(1).strip()

    # GSTIN / Tax ID
    gstin_match = re.search(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b", text)
    if gstin_match:
        result["gstin"] = gstin_match.group(0)
        result["validations"].append({
            "code": "VALID_GSTIN_FORMAT",
            "title": "Valid GSTIN Tax ID Format",
            "description": f"GSTIN '{result['gstin']}' conforms to statutory tax registration structure.",
            "severity": "VERIFIED",
            "weight": 0
        })

    # Vendor Name
    vendor_match = re.search(r"(?:from|billed\s*by|seller|vendor)\s*[:\-]?\s*([A-Za-z0-9 .,&'-]{3,50})", text, re.IGNORECASE)
    if vendor_match:
        result["vendor_name"] = clean_value(vendor_match.group(1).split("\n")[0])

    return result