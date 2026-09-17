import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Read image
image = cv2.imread("uploads/test.jpg")

# Resize
image = cv2.resize(
    image,
    None,
    fx=2,
    fy=2,
    interpolation=cv2.INTER_CUBIC
)

# Grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Threshold
processed = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU
)[1]

# OCR
text = pytesseract.image_to_string(
    processed,
    config="--psm 6"
)
# OCR specifically for numbers and dates
number_text = pytesseract.image_to_string(
    image,
    config='--psm 6 -c tessedit_char_whitelist=0123456789/-'
)
print("\n===== RAW OCR =====\n")
print(text)
# -------------------------
# FIELD EXTRACTION
# -------------------------

import re

# Clean OCR text
clean_text = text.replace("\n", " ")

# -------------------------
# DATES
# -------------------------

dates = re.findall(
    r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
    text
)

# -------------------------
# NUMBERS
# -------------------------

# Find sequences containing digits and possible OCR spaces
raw_numbers = re.findall(
    r"\b(?:\d[\s-]?){10,16}\b",
    clean_text
)

numbers = []

for num in raw_numbers:
    num = re.sub(r"[\s-]", "", num)

    if 10 <= len(num) <= 16:
        numbers.append(num)

# Remove duplicates
numbers = list(dict.fromkeys(numbers))

# -------------------------
# PIN CODES
# -------------------------

pincodes = re.findall(
    r"\b\d{6}\b",
    clean_text
)

pincodes = list(dict.fromkeys(pincodes))

# -------------------------
# POSSIBLE NAMES
# -------------------------

name_matches = re.findall(
    r"(?:Name|S/O|D/O|W/O|C/O)\s*[:\-]?\s*([A-Za-z][A-Za-z ]{2,50})",
    text,
    re.IGNORECASE
)

# -------------------------
# DISPLAY
# -------------------------

print("\n===== EXTRACTED FIELDS =====")

print("\nDates:")
for date in dates:
    print(" -", date)

print("\nPossible ID / Long Numbers:")
for number in numbers:
    print(" -", number)

print("\nPIN codes:")
for pin in pincodes:
    print(" -", pin)

print("\nPossible names:")
for name in name_matches:
    print(" -", name.strip())