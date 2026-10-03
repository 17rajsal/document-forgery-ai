"""
Proofly Automated Verification & Test Suite
Tests all core Proofly multimodal investor safety and forensic engines:
- QR code and UPI parsing
- Typo-squatting domain detection
- AI erase and generative inpainting detection
- Financial field tampering and semantic contradictions
- Claim extraction and scam language detection
- Regulatory evidence verification
- Identity consistency engine
- Multi-signal evidence fusion
- Plain-language and Hindi voice generation
- Deterministic demo scenario execution
"""

import sys
import os
import unittest
from PIL import Image, ImageDraw

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import main
from proofly.qr_url_analyzer import parse_upi_uri, analyze_url, detect_and_decode_qrcodes
from proofly.ai_erase_detector import detect_ai_erase_and_inpainting
from proofly.financial_field_analyzer import analyze_financial_fields
from proofly.claim_extractor import extract_claims_from_text
from proofly.evidence_checker import verify_claims_against_evidence
from proofly.identity_consistency import build_entity_graph
from proofly.fusion_engine import fuse_proofly_evidence
from proofly.plain_explainer import generate_plain_explanations
from proofly.demo_scenarios import DEMO_SCENARIOS, render_demo_canvas


class TestProoflySuite(unittest.TestCase):

    def test_01_qr_and_upi_parsing(self):
        """Test UPI link parsing and personal handle flagging."""
        raw_upi = "upi://pay?pa=9876543210@ybl&pn=RajeshKumar&am=25000&cu=INR"
        parsed = parse_upi_uri(raw_upi)
        self.assertTrue(parsed["is_upi"])
        self.assertEqual(parsed["payee_address"], "9876543210@ybl")
        self.assertEqual(parsed["amount"], "25000")
        self.assertTrue(parsed["is_personal_handle"])

    def test_02_url_typosquatting_detection(self):
        """Test detection of regulatory lookalike domains and insecure HTTP."""
        res = analyze_url("http://sebi-invest-secure.xyz/kyc", claimed_entity="SEBI")
        self.assertTrue(res["typosquatting_detected"])
        self.assertTrue(res["has_suspicious_tld"])
        self.assertFalse(res["is_https"])
        risk_codes = [f["code"] for f in res["risk_flags"]]
        self.assertIn("REGULATORY_TYPOSQUATTING", risk_codes)
        self.assertIn("SUSPICIOUS_DOMAIN_TLD", risk_codes)
        self.assertIn("INSECURE_HTTP_PROTOCOL", risk_codes)

    def test_03_ai_inpainting_detector_on_clean_image(self):
        """Test AI erase detector produces clean results on non-tampered canvas."""
        canvas = Image.new("RGB", (600, 600), color=(245, 245, 245))
        res = detect_ai_erase_and_inpainting(canvas)
        self.assertTrue(res["available"])
        self.assertFalse(res["inpainting_detected"])
        self.assertEqual(res["regions_count"], 0)

    def test_04_financial_field_semantic_contradiction(self):
        """Test detection of numeric amount vs. verbal words mismatch."""
        text = "Allotment amount: ₹90,000 only. Total in words: ten thousand rupees only."
        words = [
            {"text": "₹90,000", "x": 100, "y": 100, "w": 80, "h": 20},
            {"text": "ten", "x": 100, "y": 150, "w": 30, "h": 20},
            {"text": "thousand", "x": 140, "y": 150, "w": 60, "h": 20}
        ]
        res = analyze_financial_fields(text, words)
        self.assertTrue(res["has_critical_field_concern"])
        self.assertTrue(len(res["semantic_contradictions"]) > 0)
        self.assertEqual(res["semantic_contradictions"][0]["code"], "SEMANTIC_AMOUNT_MISMATCH")

    def test_05_claim_and_scam_language_extraction(self):
        """Test high-risk claim extraction: guaranteed returns, SEBI approval, urgency."""
        text = "Guaranteed 30% monthly return! SEBI approved scheme. Act now, only 5 slots left! Pay immediately."
        words = [{"text": "Guaranteed", "x": 50, "y": 50, "w": 100, "h": 20}]
        claims = extract_claims_from_text(text, words, claimed_entity="Apex Wealth")
        self.assertGreaterEqual(len(claims), 4)
        categories = [c["category"] for c in claims]
        self.assertIn("GUARANTEED_RETURN_CLAIMS", categories)
        self.assertIn("REGULATOR_AUTHORITY_CLAIMS", categories)
        self.assertIn("URGENCY_FOMO", categories)
        self.assertIn("PAYMENT_PRESSURE", categories)

    def test_06_evidence_verification(self):
        """Test that guaranteed return and regulator endorsement yield conflicting evidence."""
        claims = [
            {"claim_id": "c1", "exact_text": "Guaranteed 30% return", "category": "GUARANTEED_RETURN_CLAIMS"},
            {"claim_id": "c2", "exact_text": "SEBI approved scheme", "category": "REGULATOR_AUTHORITY_CLAIMS"}
        ]
        ev = verify_claims_against_evidence(claims)
        self.assertEqual(len(ev), 2)
        for item in ev:
            self.assertEqual(item["evidence_status"], "Conflicting evidence")
            self.assertTrue("SEBI" in item["official_source"])

    def test_07_identity_consistency_mismatch(self):
        """Test corporate entity using Gmail and personal UPI."""
        text = "Document from HDFC Mutual Fund. Contact us at hdfchelpdesk99@gmail.com"
        qr = [{"is_upi": True, "upi_details": {"payee_address": "9876543210@paytm", "payee_name": "Suresh Kumar"}}]
        graph = build_entity_graph(text, qr, urls=[], claimed_entity="HDFC Mutual Fund")
        self.assertFalse(graph["is_consistent"])
        self.assertEqual(graph["mismatch_count"], 2)

    def test_08_multi_signal_fusion_high_concern(self):
        """Test fusion engine correctly aggregates multiple red flags into HIGH concern."""
        base_forensics = {"risk_score": 65}
        ai_inpainting = {"inpainting_detected": True, "regions_count": 1}
        financial_fields = {
            "semantic_contradictions": [{"title": "Amount Mismatch", "description": "Mismatch", "severity": "CRITICAL"}],
            "tampered_fields": []
        }
        claims = [{"category": "GUARANTEED_RETURN_CLAIMS", "exact_text": "Guaranteed", "title": "Guaranteed", "explanation": "Prohibited", "severity": "CRITICAL"}]
        evidence = [{"evidence_status": "Conflicting evidence"}]
        qr = [{"risk_flags": [{"title": "Personal UPI", "description": "Personal handle", "severity": "CRITICAL"}]}]
        urls = []
        identity = {"is_consistent": False, "mismatches": [{"title": "Email Mismatch", "description": "Gmail", "severity": "CRITICAL"}]}

        fusion = fuse_proofly_evidence(
            base_forensics, ai_inpainting, financial_fields, claims, evidence, qr, urls, identity
        )
        self.assertEqual(fusion["concern_level"], "HIGH")
        self.assertGreaterEqual(fusion["total_risk_score"], 80)
        self.assertTrue(len(fusion["key_findings"]) >= 5)

    def test_09_plain_and_hindi_explanations(self):
        """Test generation of simple English, Hindi narrative, and voice scripts."""
        assessment = {"concern_level": "HIGH"}
        claims = [{"category": "GUARANTEED_RETURN_CLAIMS", "exact_text": "30% guaranteed"}]
        financial_fields = {"semantic_contradictions": [], "tampered_fields": []}
        identity = {"mismatches": []}
        qr = []
        ai_inpainting = {"inpainting_detected": False}

        exp = generate_plain_explanations(assessment, claims, financial_fields, identity, qr, ai_inpainting)
        self.assertIn("guaranteed", exp["simple_explanation_en"].lower())
        self.assertIn("guaranteed", exp["simple_explanation_hi"].lower())
        self.assertTrue(len(exp["voice_script_hi"]) > 20)
        self.assertTrue(len(exp["safe_steps"]) == 4)

    def test_10_deterministic_kavita_demo_execution(self):
        """Test complete execution of Kavita WhatsApp demo scenario via backend main."""
        res = main.analyze_proofly_demo("kavita_whatsapp_scam")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["concern_level"], "HIGH")
        self.assertIn("proofly", res)
        dossier = res["proofly"]
        self.assertEqual(dossier["assessment"]["concern_level"], "HIGH")
        self.assertGreater(len(dossier["visual_evidence_map"]), 0)
        self.assertIn("demo_scenario_info", res)
        self.assertEqual(res["demo_scenario_info"]["demo_id"], "kavita_whatsapp_scam")


if __name__ == "__main__":
    unittest.main()
