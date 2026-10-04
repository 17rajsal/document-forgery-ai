import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from proofly.entity_verifier import verify_intermediary, validate_registration_format
from proofly.text_url_analyzer import analyze_scam_language, analyze_url_domain, analyze_text_and_url_submission
from proofly.demo_scenarios import DEMO_SCENARIOS, render_demo_canvas


class TestInvestorSafety(unittest.TestCase):

    def test_entity_verification_registered(self):
        """Official SEBI registered broker should be VERIFIED."""
        res = verify_intermediary(
            claimed_entity="Zerodha Broking Limited",
            registration_number="INZ000031633"
        )
        self.assertEqual(res["status"], "VERIFIED")
        self.assertIn("recognized", res["verdict"].lower())
        self.assertEqual(res["matched_record"]["regulator"], "SEBI")

    def test_entity_verification_impersonation(self):
        """Claiming a real registration number under a fake company name must be flagged."""
        res = verify_intermediary(
            claimed_entity="Scam Forex Traders Ltd",
            registration_number="INZ000031633"
        )
        self.assertEqual(res["status"], "NOT VERIFIED")
        self.assertTrue("Zerodha" in res["verdict"] and "Scam Forex Traders Ltd" in res["verdict"])
        self.assertTrue(any("impersonation" in c.lower() for c in res["concerns"]))

    def test_entity_verification_invalid_format(self):
        """Malformed registration strings should trigger NOT VERIFIED."""
        res = verify_intermediary(
            claimed_entity="Random Group",
            registration_number="INVALID_REG_123"
        )
        self.assertEqual(res["status"], "NOT VERIFIED")

    def test_entity_verification_unverified(self):
        """Valid format but not in public registry mirror should return UNABLE TO VERIFY without fabricating."""
        res = verify_intermediary(
            claimed_entity="Unknown Advisory",
            registration_number="INZ999888777"
        )
        self.assertEqual(res["status"], "UNABLE TO VERIFY")
        self.assertIn("sebi.gov.in", res["verdict"])

    def test_scam_language_detection(self):
        """High-risk promises must be detected with high score."""
        sample_scam = (
            "EXCLUSIVE PRE-IPO OFFER! Invest ₹50,000 and get ₹80,000 guaranteed 30% monthly return! "
            "100% risk free. SEBI approved registration INZ999888777. Only 2 slots left, transfer now!"
        )
        res = analyze_scam_language(sample_scam)
        self.assertGreaterEqual(res["score"], 80)
        self.assertEqual(res["level"], "HIGH")
        self.assertTrue(res["has_critical"])
        self.assertGreaterEqual(res["found_count"], 3)

    def test_scam_language_clean_text(self):
        """Authentic disclaimer text should yield 0 or low scam score."""
        clean_text = (
            "Mutual fund investments are subject to market risks. Please read all scheme related "
            "documents carefully before investing. Past performance is not indicative of future returns."
        )
        res = analyze_scam_language(clean_text)
        self.assertLessEqual(res["score"], 15)
        self.assertEqual(res["level"], "LOW")

    def test_url_domain_analysis_lookalike(self):
        """Typosquatting Indian institutions should trigger HIGH risk and lookalike flag."""
        res = analyze_url_domain("https://zerodha-bonus-invest.xyz")
        self.assertEqual(res["level"], "HIGH")
        self.assertTrue(res["is_lookalike"])
        self.assertTrue(any("lookalike" in c.lower() or "typosquatting" in c.lower() for c in res["concerns"]))

    def test_composite_text_analysis_breakdown(self):
        """Full text submission returns 4-component breakdown, Hindi & English explanations, and no stock advice."""
        scam_text = (
            "Invest ₹50,000 to earn ₹80,000 in 30 days! SEBI approved advisor. "
            "Send money to UPI vikram.personal88@okaxis or visit https://zerodha-bonus-invest.xyz"
        )
        res = analyze_text_and_url_submission(text=scam_text)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["investor_scam_risk"]["risk_level"], "HIGH RISK")
        self.assertIn("document_integrity", res["component_breakdown"])
        self.assertIn("scam_language", res["component_breakdown"])
        self.assertIn("url_domain_risk", res["component_breakdown"])
        self.assertIn("entity_verification", res["component_breakdown"])
        self.assertIn("en", res["why_flagged"])
        self.assertIn("hi", res["why_flagged"])
        self.assertGreaterEqual(len(res["why_flagged"]["en"]), 2)

    def test_benchmark_demo_scenario_rendered(self):
        """Primary demo scenario canvas generates cleanly with watermark and metadata."""
        self.assertIn("sebi_nsdl_50k_80k_certificate", DEMO_SCENARIOS)
        scenario = DEMO_SCENARIOS["sebi_nsdl_50k_80k_certificate"]
        self.assertIn("₹80,000 within 30 days", scenario["claims_mock"][0]["exact_text"])
        self.assertEqual(scenario["qr_mock"]["upi_details"]["payee_address"], "vikram.personal88@okaxis")


if __name__ == "__main__":
    unittest.main()
