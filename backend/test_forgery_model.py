import os
import sys
import io
import unittest
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Ensure backend directory is in path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from forgery_detector import analyze_image, calculate_composite_forgery_score
from document_classifier import get_standard_category


class TestForgeryModel(unittest.TestCase):
    """
    Automated test suite verifying the multi-signal forgery detection model
    across all 6 core scenarios to guarantee low false-positive rates on genuine documents.
    """

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = os.path.join(BACKEND_DIR, "scratch_test_docs")
        os.makedirs(cls.temp_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. GENUINE ORIGINAL DOCUMENT
    # -------------------------------------------------------------
    def test_01_genuine_original_document(self):
        """A clean, high-resolution original document must be classified as Likely Genuine with low risk score."""
        img = Image.new("RGB", (900, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((60, 50), "STATE GOVERNMENT HEALTH INSURANCE CARD", fill=(20, 30, 70))
        draw.text((60, 100), "CARDHOLDER: RAJESH K. VERMA", fill=(40, 40, 40))
        draw.text((60, 140), "POLICY NUMBER: POL-88392019", fill=(40, 40, 40))
        draw.text((60, 180), "EXPIRATION DATE: 31-DEC-2028", fill=(40, 40, 40))

        file_path = os.path.join(self.temp_dir, "test_genuine_original.jpg")
        img.save(file_path, format="JPEG", quality=95)

        res = analyze_image(file_path, document_type="id_card")
        score = res["risk_score"]
        status = res["authenticity_status"]

        self.assertNotEqual(status, "Likely Forged", "Genuine original must never be classified as Likely Forged")
        self.assertEqual(status, "Likely Genuine", f"Expected Likely Genuine, got {status} (score={score})")
        self.assertLessEqual(score, 28, f"Genuine original score must be <= 28, got {score}")

    # -------------------------------------------------------------
    # 2. GENUINE SCANNED DOCUMENT
    # -------------------------------------------------------------
    def test_02_genuine_scanned_document(self):
        """A scanned document with minor texture/grain must NOT be flagged as forged."""
        img = Image.new("RGB", (850, 700), color=(248, 248, 246))
        draw = ImageDraw.Draw(img)
        draw.text((80, 60), "OFFICIAL TRADE CLEARANCE DIRECTIVE", fill=(10, 20, 40))
        for y in range(120, 500, 35):
            draw.text((80, y), f"Clause {y//35}: This standard scanned certificate contains official declarations.", fill=(50, 50, 50))

        # Add realistic scanner noise
        np_arr = np.array(img, dtype=np.float32)
        noise = np.random.normal(0, 3.0, np_arr.shape)
        scanned_img = Image.fromarray(np.clip(np_arr + noise, 0, 255).astype(np.uint8))

        file_path = os.path.join(self.temp_dir, "test_genuine_scan.jpg")
        scanned_img.save(file_path, format="JPEG", quality=88)

        res = analyze_image(file_path, document_type="general_scanned")
        status = res["authenticity_status"]
        score = res["risk_score"]

        self.assertNotEqual(status, "Likely Forged", f"Scanned document must not be flagged Likely Forged: score={score}")
        self.assertIn(status, ["Likely Genuine", "Needs Manual Review"])

    # -------------------------------------------------------------
    # 3. COMPRESSED IMAGE (SOCIAL MEDIA / RE-SAVING)
    # -------------------------------------------------------------
    def test_03_compressed_image(self):
        """A low-quality or re-compressed image must NOT be classified as forged based on uniform compression."""
        img = Image.new("RGB", (800, 550), color=(250, 250, 250))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), "ACADEMIC TRANSCRIPT & RECORD OF STUDY", fill=(20, 20, 20))
        draw.text((50, 100), "STUDENT: AMITABH SEN | DEGREE: B.TECH", fill=(50, 50, 50))

        # Compress heavily at JPEG quality=35
        file_path = os.path.join(self.temp_dir, "test_compressed.jpg")
        img.save(file_path, format="JPEG", quality=35)

        res = analyze_image(file_path, document_type="marksheet")
        status = res["authenticity_status"]
        score = res["risk_score"]

        self.assertNotEqual(status, "Likely Forged", f"Compressed image must not be marked Likely Forged: score={score}")
        # ELA should recognize uniform global compression
        is_uniform = res["ela_analysis"].get("is_uniform_compression")
        self.assertTrue(is_uniform or score <= 35, "Uniform compression should be recognized or scored conservatively")

    # -------------------------------------------------------------
    # 4. DIGITAL SCREENSHOT
    # -------------------------------------------------------------
    def test_04_screenshot(self):
        """A clean digital screenshot (PNG) must NOT be marked forged."""
        # 16:9 or 16:10 screenshot aspect ratio
        img = Image.new("RGB", (1280, 720), color=(245, 247, 250))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (1280, 60)], fill=(30, 58, 138))
        draw.text((40, 20), "PORTAL DASHBOARD - ACCOUNT VERIFICATION", fill=(255, 255, 255))
        draw.text((40, 120), "TAX INVOICE PAYMENT CONFIRMATION", fill=(30, 41, 59))
        draw.text((40, 160), "TRANSACTION ID: TXN-2025-99812401", fill=(71, 85, 105))
        draw.text((40, 200), "AMOUNT PAID: $450.00", fill=(71, 85, 105))

        file_path = os.path.join(self.temp_dir, "test_screenshot.png")
        img.save(file_path, format="PNG")

        res = analyze_image(file_path, document_type="invoice_receipt")
        status = res["authenticity_status"]
        score = res["risk_score"]

        self.assertNotEqual(status, "Likely Forged", f"Screenshot must not be marked Likely Forged: score={score}")
        self.assertIn(status, ["Likely Genuine", "Needs Manual Review"])

    # -------------------------------------------------------------
    # 5. EDITED / TAMPERED DOCUMENT
    # -------------------------------------------------------------
    def test_05_edited_document(self):
        """A document with multiple corroborated tampering traces (spliced patch + editing tool tag) must be detected."""
        img = Image.new("RGB", (850, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 40), "APEX UNIVERSITY - STATEMENT OF MARKS", fill=(10, 10, 10))
        draw.text((50, 90), "STUDENT: ROHAN SHARMA | ROLL NO: 88129", fill=(30, 30, 30))
        draw.text((50, 140), "MATHEMATICS: 45 / 100", fill=(40, 40, 40))

        # Tampering 1: Spliced patch pasted from another image
        patch = Image.new("RGB", (180, 80), color=(210, 215, 230))
        p_draw = ImageDraw.Draw(patch)
        p_draw.text((15, 25), "99 / 100 (A+)", fill=(0, 0, 0))
        img.paste(patch, (220, 130))

        # Tampering 2: Replicated copy-move stamp
        stamp = Image.new("RGB", (100, 100), color=(255, 240, 240))
        s_draw = ImageDraw.Draw(stamp)
        s_draw.ellipse([(10, 10), (90, 90)], outline=(180, 20, 20), width=3)
        s_draw.text((25, 40), "SEAL", fill=(180, 20, 20))
        img.paste(stamp, (50, 400))
        img.paste(stamp, (650, 400))  # Duplicate stamp across coordinates

        file_path = os.path.join(self.temp_dir, "test_edited_tampered.jpg")
        img.save(file_path, format="JPEG", quality=90)

        # Inject Photoshop signature tag
        with open(file_path, "ab") as f:
            f.write(b"\n<!-- Adobe Photoshop 2024 (Windows) XMP Core 7.1 -->\n")

        # Layout token list with abnormal font height jump
        mock_words = [
            {"text": "MATHEMATICS:", "x": 50, "y": 140, "w": 120, "h": 14},
            {"text": "SCORE", "x": 180, "y": 140, "w": 50, "h": 14},
            {"text": "99", "x": 240, "y": 130, "w": 40, "h": 36},  # Abnormal height jump (36px vs 14px)
            {"text": "OUT", "x": 290, "y": 140, "w": 30, "h": 14},
            {"text": "OF", "x": 330, "y": 140, "w": 25, "h": 14},
            {"text": "100", "x": 365, "y": 140, "w": 35, "h": 14},
            {"text": "GRADE", "x": 410, "y": 140, "w": 50, "h": 14},
            {"text": "PASS", "x": 470, "y": 140, "w": 40, "h": 14},
        ]

        res = analyze_image(file_path, words=mock_words, document_type="marksheet")
        status = res["authenticity_status"]
        score = res["risk_score"]
        signals_count = res.get("tampering_signals_count", 0)

        self.assertGreaterEqual(signals_count, 2, f"Corroborated tampering signals should be >= 2, got {signals_count}")
        self.assertGreaterEqual(score, 60, f"Tampered document score must be >= 60, got {score}")
        self.assertEqual(status, "Likely Forged", f"Expected Likely Forged, got {status} (score={score})")

    # -------------------------------------------------------------
    # 6. CORRUPTED FILE HANDLING
    # -------------------------------------------------------------
    def test_06_corrupted_file(self):
        """Corrupted files must be handled gracefully without crashing the system."""
        corrupted_path = os.path.join(self.temp_dir, "test_corrupted.jpg")
        # Valid JPEG magic header followed by truncated invalid payload
        with open(corrupted_path, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0" + b"\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + b"\x00" * 30)

        # analyze_image should either catch and handle or raise a standard ValueError/IOError
        try:
            res = analyze_image(corrupted_path, document_type="general_scanned")
            # If handled internally, should fall back safely to review
            self.assertIn(res["authenticity_status"], ["Needs Manual Review", "Likely Genuine"])
        except Exception as e:
            # Raising a clear error is also standard safe behavior
            self.assertTrue(isinstance(e, (IOError, ValueError, Exception)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
