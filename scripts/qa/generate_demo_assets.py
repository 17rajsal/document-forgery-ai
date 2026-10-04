"""Rebuild fictional demo fixtures only; requires already-installed Pillow.

Run from any directory. Never imports or changes the application.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo


ROOT = Path(__file__).resolve().parents[2] / "demo_samples"
DISCLAIMER = "DEMO SAMPLE — NOT A REAL FINANCIAL DOCUMENT"
CASES = [
    {
        "sample_id": "guaranteed_return",
        "title": "Fictional Moonrise Growth Sprint",
        "expected_risk": "high",
        "lines": [
            "PROOFLY DEMO INVESTMENT PLAN",
            "Plan: Fictional Moonrise Growth Sprint",
            "Invest ₹50,000. Get ₹80,000 in 30 days!",
            "Guaranteed 60% profit. Zero risk. No losses possible.",
            "Only 10 slots left — pay within 15 minutes to lock your return!",
            "Registration-style ID: DEMO-INV-83921 (fabricated)",
            "Website: https://moonrise-fast-profit.example/activate",
            "QR payload text (not a scannable payment code):",
            "DEMO_ONLY|PLAN=MOONRISE|AMOUNT_INR=50000|REFERENCE=DEMO-83921",
            "Fictional promotional message for testing; do not send money.",
        ],
        "expected_findings": ["Unrealistic guaranteed return", "False zero-risk framing", "Urgency and scarcity pressure", "Fabricated registration-style identifier"],
        "expected_ocr_fields": {"plan_name": "Fictional Moonrise Growth Sprint", "investment_amount_inr": 50000, "promised_payout_inr": 80000, "duration_days": 30, "claimed_profit_percent": 60, "registration_id": "DEMO-INV-83921", "url": "https://moonrise-fast-profit.example/activate", "qr_payload_text": "DEMO_ONLY|PLAN=MOONRISE|AMOUNT_INR=50000|REFERENCE=DEMO-83921"},
        "expected_scam_signals": ["guaranteed_returns", "unrealistic_returns", "zero_risk_claim", "urgency", "scarcity", "unverified_registration"],
    },
    {
        "sample_id": "broker_impersonation",
        "title": "Fictional CedarBridge broker verification alert",
        "expected_risk": "high",
        "lines": [
            "PROOFLY DEMO BROKER MESSAGE",
            "Sender: Fictional CedarBridge Investor Clearance Desk",
            "CLAIM: SEBI-approved broker; official regulator verification partner.",
            "Claimed registration ID: DEMO-BROKER-472910 (fabricated)",
            "Your investment account will be frozen in 20 minutes.",
            "Verify immediately and pay a refundable ₹2,499 clearance fee.",
            "Website: https://sebi-clearance.cedarbridge-check.example/verify",
            "Reply address: urgent-desk@cedarbridge-mail.example",
            "We claim regulator authority but request payment on our own portal.",
            "This fictional broker is not affiliated with SEBI or any regulator.",
            "No real account, registration, payment destination, or approval exists.",
        ],
        "expected_findings": ["Claimed regulator affiliation without evidence", "Regulator name in an unrelated domain", "Threat of account freezing", "Urgent verification fee request", "Sender and website domains differ"],
        "expected_ocr_fields": {"sender": "Fictional CedarBridge Investor Clearance Desk", "claimed_regulator": "SEBI", "registration_id": "DEMO-BROKER-472910", "requested_fee_inr": 2499, "deadline_minutes": 20, "url": "https://sebi-clearance.cedarbridge-check.example/verify", "reply_address": "urgent-desk@cedarbridge-mail.example"},
        "expected_scam_signals": ["regulator_impersonation", "broker_impersonation", "lookalike_domain", "account_freeze_threat", "urgent_payment_request", "sender_domain_mismatch"],
    },
    {
        "sample_id": "educational_control",
        "title": "Fictional investing education handout",
        "expected_risk": "low",
        "lines": [
            "PROOFLY DEMO LEARNING NOTE",
            "Topic: Understanding investment risk",
            "Prepared by: Fictional Riverstone Learning Circle",
            "Investments may rise or fall in value. Returns are not guaranteed.",
            "Compare fees, liquidity, and risk before making a decision.",
            "Diversification can reduce concentration risk; it cannot remove all risk.",
            "Take time to read the product information and ask questions.",
            "This handout offers general education, not a specific investment plan.",
            "It requests no payment, account verification, or personal information.",
            "There is no offer, deadline, registration claim, or promised payout.",
        ],
        "expected_findings": [],
        "expected_ocr_fields": {"topic": "Understanding investment risk", "publisher": "Fictional Riverstone Learning Circle", "document_type": "educational handout"},
        "expected_scam_signals": [],
    },
]


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def font(size, bold=False):
    # Windows fonts provide the rupee sign and em dash used in these fixtures.
    names = ["C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
             "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    raise RuntimeError("A font supporting ₹ and — is required; no assets regenerated.")


def document(lines):
    image = Image.new("RGB", (1800, 1100), "#ffffff")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 1780, 1080), outline="#555555", width=2)
    draw.text((60, 50), DISCLAIMER, font=font(39, True), fill="#9a2323")
    for i, line in enumerate(lines):
        draw.text((60, 150 + 61 * i), line, font=font(29), fill="#222222")
    draw.text((60, 1015), "Synthetic OCR/QA fixture • All entities and identifiers are fictional.", font=font(25), fill="#555555")
    return image


def save_image(image, path):
    info = PngInfo()
    info.add_itxt("disclaimer", DISCLAIMER)
    image.save(path, pnginfo=info)


def main():
    font(29)  # Fail before writing if no suitable font is available.
    for directory in ("text", "metadata", "images"):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    assets = []
    categories = ["scam_language", "impersonation", "normal_control"]
    for case, category in zip(CASES, categories):
        sample_id = case["sample_id"]
        for suffix, directory, purpose in [("txt", "text", "Plain-text NLP/OCR reference"), ("png", "images", "Synthetic document for OCR"), ("json", "metadata", "QA expectations only; not AI output")]:
            assets.append({"path": f"{directory}/{sample_id}.{suffix}", "sample_id": sample_id, "category": category, "purpose": purpose})
        (ROOT / "text" / f"{sample_id}.txt").write_text(DISCLAIMER + "\n\n" + "\n".join(case["lines"]) + "\n", encoding="utf-8")
        metadata = {key: value for key, value in case.items() if key != "lines"}
        metadata.update({"disclaimer": DISCLAIMER, "expectation_type": "QA/demo expectations only — not production AI results", "notes": ["All names and registration identifiers are fictional; .example domains are placeholders.", "Expected risk is a fixture label, not an AI verdict or financial advice.", "Assess context and negation; the educational control mentions risk and guarantees without promoting them."]})
        save_json(ROOT / "metadata" / f"{sample_id}.json", metadata)
        save_image(document(case["lines"]), ROOT / "images" / f"{sample_id}.png")

    original = document(["PROOFLY DEMO AMOUNT RECORD", "Record ID: DEMO-AMOUNT-001", "Investment Amount: ₹5,000", "Purpose: Synthetic document manipulation testing only.", "No transaction, investor, payment account, or investment offer exists."])
    save_image(original, ROOT / "images" / "original_demo.png")
    tampered = original.copy()
    draw = ImageDraw.Draw(tampered)
    # Exclusive right/bottom bounds; patch covers only the amount, not its label.
    amount_x = 60 + int(ImageDraw.Draw(original).textlength("Investment Amount: ", font=font(29)))
    box = [amount_x, 268, amount_x + 200, 314]
    draw.rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill="#f4f1e9")
    draw.text((amount_x + 2, 274), "₹50,000", font=font(31, True), fill="#343434")
    save_image(tampered, ROOT / "images" / "tampered_demo.png")
    save_json(ROOT / "metadata" / "tampering.json", {
        "sample_id": "document_tampering", "title": "Synthetic amount replacement pair", "disclaimer": DISCLAIMER,
        "expected_risk": "medium", "expectation_type": "QA/demo expectations only — not production AI results",
        "expected_findings": ["Localized amount replacement", "Different font weight, size, baseline, and background within patch"],
        "expected_ocr_fields": {"original_investment_amount_inr": 5000, "tampered_investment_amount_inr": 50000},
        "expected_scam_signals": [],
        "original_path": "images/original_demo.png", "tampered_path": "images/tampered_demo.png",
        "change": {"field": "Investment Amount", "before": "₹5,000", "after": "₹50,000", "bounding_box_xyxy": box, "coordinate_convention": "pixels from top left; right and bottom exclusive", "image_dimensions": [1800, 1100], "visual_changes": ["29px regular to 31px bold", "2px right/down offset", "white to pale beige background", "slightly lighter text"]},
        "notes": ["The medium label represents a synthetic review fixture, not a calibrated fraud score.", "This pair is for testing; the application may or may not detect the edit.", "Only the declared patch differs; no real financial document is used."]})
    for path, purpose in [("images/original_demo.png", "Original amount ₹5,000"), ("images/tampered_demo.png", "Edited amount ₹50,000 with localized visual mismatch"), ("metadata/tampering.json", "Exact patch coordinates and before/after values")]:
        assets.append({"path": path, "sample_id": "document_tampering", "category": "document_tampering", "purpose": purpose})
    save_json(ROOT / "manifest.json", {"schema_version": 1, "disclaimer": DISCLAIMER, "purpose": "Standalone fictional fixtures; expectations are not production AI results.", "assets": assets, "notes": ["Paths are relative to demo_samples. This manifest inventories the sample payloads.", "Run python scripts/qa/check_demo_assets.py; Pillow is optional for pixel validation.", "Rebuild with python scripts/qa/generate_demo_assets.py (Pillow required).", "No application integration or live-domain checks are performed."]})
    print(f"Created {len(assets)} demo payloads and manifest in {ROOT}")


if __name__ == "__main__":
    main()
