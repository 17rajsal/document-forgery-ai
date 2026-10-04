"""
Proofly Deterministic Demo Scenarios
Provides high-fidelity, deterministic demo cases for the SANGYAN Hackathon,
including the Kavita WhatsApp Pre-IPO scam journey, traditional forgery,
AI inpainting alteration, and clean genuine financial statement.
"""

from typing import Dict, Any, List


DEMO_SCENARIOS = {
    "sebi_nsdl_50k_80k_certificate": {
        "id": "sebi_nsdl_50k_80k_certificate",
        "title": "DEMO SAMPLE: Guaranteed 30-Day Certificate (₹50k to ₹80k)",
        "category": "High-Yield Scam (SEBI/NSDL Impersonation)",
        "filename": "DEMO_SAMPLE_Guaranteed_Return_Certificate.jpg",
        "document_type": "Priority Investment Certificate",
        "persona": "Retail Investor targeted with fake SEBI/NSDL guaranteed profit scheme",
        "claimed_entity": "Apex Growth Asset Management (SEBI / NSDL Authorized)",
        "preview_badge": "HIGH RISK (Demo Sample)",
        "sample_text": (
            "[DEMO SAMPLE - NOT AN OFFICIAL INSTITUTIONAL DOCUMENT]\n"
            "APEX GROWTH ASSET MANAGEMENT\n"
            "Priority Allotment & Assured Return Certificate\n"
            "Investor Name: Smt. Sunita Devi | Allotment ID: APX-9921\n"
            "Investment Amount: ₹50,000.00\n"
            "Guaranteed Return: Receive ₹80,000 within 30 days (60% Assured Profit)\n"
            "Status: SEBI & NSDL approved priority quota allotment.\n"
            "Claimed SEBI Registration: INZ999888777 (Unverified)\n"
            "Act now! Only 3 priority allotment slots remaining today.\n"
            "Pay ₹50,000 immediately to lock allocation before window expires.\n"
            "Scan QR code below or pay via UPI: vikram.personal88@okaxis\n"
            "Payee Name: Vikram Malhotra | Account: 998877665544\n"
            "Support: verify@sebi-investor-portal.xyz | Call: +91 9123456780\n"
            "[DEMO SAMPLE - SANGYAN INVESTOR RESILIENCE HACKATHON]"
        ),
        "qr_mock": {
            "is_upi": True,
            "raw_content": "upi://pay?pa=vikram.personal88@okaxis&pn=VikramMalhotra&am=50000&cu=INR",
            "bbox": {"x": 680, "y": 920, "w": 260, "h": 260},
            "upi_details": {
                "payee_address": "vikram.personal88@okaxis",
                "payee_name": "Vikram Malhotra",
                "amount": "50000",
                "is_personal_handle": True
            }
        },
        "critical_fields_mock": [
            {
                "field_type": "MONETARY_AMOUNT",
                "raw_text": "₹50,000.00",
                "bbox": {"x": 380, "y": 420, "w": 180, "h": 40},
                "tamper_concern": "HIGH",
                "finding": "Amount field exhibits sharp gradient discontinuity and local compression variance"
            },
            {
                "field_type": "RETURN_PERCENTAGE",
                "raw_text": "Receive ₹80,000 within 30 days (60% Assured Profit)",
                "bbox": {"x": 120, "y": 480, "w": 520, "h": 40},
                "tamper_concern": "HIGH",
                "finding": "Prohibited guaranteed yield claim directly contradicting SEBI IA Regulations"
            }
        ],
        "claims_mock": [
            {
                "claim_id": "c_g1",
                "exact_text": "Receive ₹80,000 within 30 days (60% Assured Profit)",
                "category": "GUARANTEED_RETURN_CLAIMS",
                "severity": "CRITICAL",
                "title": "Unrealistic Guaranteed Return Claim",
                "bbox": {"x": 120, "y": 480, "w": 520, "h": 40}
            },
            {
                "claim_id": "c_r1",
                "exact_text": "SEBI & NSDL approved priority quota allotment",
                "category": "REGULATOR_AUTHORITY_CLAIMS",
                "severity": "CRITICAL",
                "title": "False Statutory Regulator Endorsement",
                "bbox": {"x": 120, "y": 540, "w": 460, "h": 36}
            },
            {
                "claim_id": "c_u1",
                "exact_text": "Act now! Only 3 priority allotment slots remaining today",
                "category": "URGENCY_FOMO",
                "severity": "HIGH",
                "title": "Urgency / FOMO Pressure Tactic",
                "bbox": {"x": 120, "y": 660, "w": 480, "h": 36}
            }
        ],
        "identity_mock": {
            "claimed": "Apex Growth Asset Management",
            "email": "verify@sebi-investor-portal.xyz",
            "upi_payee": "vikram.personal88@okaxis (Vikram Malhotra)",
            "registration": "INZ999888777"
        }
    },
    "kavita_whatsapp_scam": {
        "id": "kavita_whatsapp_scam",
        "title": "Kavita's Case: WhatsApp Pre-IPO Scam PDF",
        "category": "Investment WhatsApp Fraud",
        "filename": "Apex_PreIPO_Allotment_Letter.pdf",
        "document_type": "Investment Allocation Letter",
        "persona": "Kavita (Tier-2 Bharat, receives lucrative WhatsApp investment offer)",
        "claimed_entity": "Apex Wealth Capital Advisory",
        "preview_badge": "High Verification Concern",
        "sample_text": (
            "APEX WEALTH CAPITAL ADVISORY\n"
            "Pre-IPO Institutional Allocation Allotment Advice\n"
            "Exclusive pre-IPO opportunity for retail priority members!\n"
            "Status: SEBI approved institutional quota.\n"
            "Guaranteed 30% return per month assured.\n"
            "Allocated Quantity: 500 Shares | Total Allotment Amount: ₹25,000\n"
            "Act now! Only 5 slots left in current allotment window.\n"
            "Pay immediately to secure allocation before window closes.\n"
            "Scan QR code below or pay via UPI: rahul.invest99@okaxis\n"
            "Support: apexwealthhelp@gmail.com | Helpline: +91 9876543210"
        ),
        "qr_mock": {
            "is_upi": True,
            "raw_content": "upi://pay?pa=rahul.invest99@okaxis&pn=RahulSharma&am=25000&cu=INR",
            "bbox": {"x": 680, "y": 920, "w": 260, "h": 260},
            "upi_details": {
                "payee_address": "rahul.invest99@okaxis",
                "payee_name": "Rahul Sharma",
                "amount": "25000",
                "is_personal_handle": True
            }
        },
        "critical_fields_mock": [
            {
                "field_type": "MONETARY_AMOUNT",
                "raw_text": "₹25,000",
                "bbox": {"x": 480, "y": 510, "w": 160, "h": 40},
                "tamper_concern": "HIGH",
                "finding": "Typography anti-aliasing sharpness disparity vs surrounding header"
            },
            {
                "field_type": "RETURN_PERCENTAGE",
                "raw_text": "30% return per month",
                "bbox": {"x": 120, "y": 420, "w": 340, "h": 36},
                "tamper_concern": "HIGH",
                "finding": "Statutorily prohibited guaranteed return promise"
            }
        ],
        "claims_mock": [
            {
                "claim_id": "c1",
                "exact_text": "Guaranteed 30% return per month assured",
                "category": "GUARANTEED_RETURN_CLAIMS",
                "severity": "CRITICAL",
                "title": "Unrealistic Guaranteed Return Claim",
                "bbox": {"x": 120, "y": 420, "w": 480, "h": 38}
            },
            {
                "claim_id": "c2",
                "exact_text": "SEBI approved institutional quota",
                "category": "REGULATOR_AUTHORITY_CLAIMS",
                "severity": "CRITICAL",
                "title": "Statutory Authority Endorsement Claim",
                "bbox": {"x": 120, "y": 350, "w": 410, "h": 36}
            },
            {
                "claim_id": "c3",
                "exact_text": "Act now! Only 5 slots left",
                "category": "URGENCY_FOMO",
                "severity": "HIGH",
                "title": "Artificial Urgency & Scarcity (FOMO)",
                "bbox": {"x": 120, "y": 580, "w": 320, "h": 34}
            },
            {
                "claim_id": "c4",
                "exact_text": "Pay immediately to secure allocation",
                "category": "PAYMENT_PRESSURE",
                "severity": "HIGH",
                "title": "Immediate Transfer Request",
                "bbox": {"x": 120, "y": 640, "w": 440, "h": 36}
            }
        ],
        "identity_mock": {
            "claimed": "Apex Wealth Capital Advisory",
            "email": "apexwealthhelp@gmail.com",
            "qr_payee": "rahul.invest99@okaxis (Rahul Sharma)",
            "phone": "+91 9876543210"
        }
    },

    "traditional_altered_bank_slip": {
        "id": "traditional_altered_bank_slip",
        "title": "Traditional Tampering: Overwritten Amount Deposit Slip",
        "category": "Bank Slip Alteration",
        "filename": "SBI_Deposit_Receipt_Modified.jpg",
        "document_type": "Bank Counterfoil / Deposit Slip",
        "persona": "Accounting Audit / Senior Investor verifying payment slip",
        "claimed_entity": "State Bank of India",
        "preview_badge": "High Verification Concern",
        "sample_text": (
            "STATE BANK OF INDIA - CASH DEPOSIT RECEIPT\n"
            "Branch: Connaught Place, New Delhi\n"
            "Date: 12/09/2026\n"
            "Account No: 30982245190\n"
            "Deposited by: Ramesh Chand\n"
            "Amount in Figures: ₹90,000\n"
            "Amount in Words: Ten Thousand Rupees Only\n"
            "Received Cashier: S. Sharma"
        ),
        "critical_fields_mock": [
            {
                "field_type": "MONETARY_AMOUNT",
                "raw_text": "₹90,000",
                "bbox": {"x": 380, "y": 380, "w": 180, "h": 45},
                "tamper_concern": "HIGH",
                "finding": "First digit '9' pasted over original '1' with background noise border"
            }
        ],
        "claims_mock": [],
        "semantic_contradiction_mock": {
            "numeric": 90000,
            "verbal": 10000,
            "title": "Severe Numeric vs. Verbal Amount Contradiction"
        }
    },

    "ai_erased_dividend_receipt": {
        "id": "ai_erased_dividend_receipt",
        "title": "AI Erase & Inpainting: Generative Fill Tax Certificate",
        "category": "Generative Fill / AI Erase",
        "filename": "TCS_Dividend_Warrant_Erased.png",
        "document_type": "Dividend Payment Certificate",
        "persona": "Individual Shareholder checking dividend credit advice",
        "claimed_entity": "Tata Consultancy Services Ltd",
        "preview_badge": "Moderate Verification Concern",
        "sample_text": (
            "TATA CONSULTANCY SERVICES LIMITED\n"
            "DIVIDEND PAYMENT ADVICE - FY 2025-26\n"
            "Folio / DP ID: IN300126-10293847\n"
            "Warrant No: DW-90182\n"
            "Payment Date: 28/08/2026\n"
            "Bank Account Credited: 50100492817264\n"
            "Net Dividend Paid: ₹14,250.00\n"
            "TDS Deducted: ₹1,580.00"
        ),
        "ai_inpainting_mock": {
            "inpainting_detected": True,
            "regions_count": 1,
            "bbox": {"x": 340, "y": 410, "w": 280, "h": 50},
            "finding": "Unnatural high-frequency smoothing and missing scanner fiber grain over account number"
        },
        "critical_fields_mock": [],
        "claims_mock": []
    },

    "genuine_mutual_fund_statement": {
        "id": "genuine_mutual_fund_statement",
        "title": "Genuine Baseline: HDFC AMC Mutual Fund Statement",
        "category": "Authentic Statement",
        "filename": "HDFC_Balanced_Advantage_Statement.pdf",
        "document_type": "Mutual Fund Account Statement",
        "persona": "Retail Investor reviewing authentic quarterly statement",
        "claimed_entity": "HDFC Asset Management Company Ltd",
        "preview_badge": "Low Verification Concern",
        "sample_text": (
            "HDFC MUTUAL FUND - CONSOLIDATED ACCOUNT STATEMENT\n"
            "HDFC Asset Management Company Limited\n"
            "SEBI Regn. No.: MF/044/00/6\n"
            "Investor Name: Sunita Devi | Folio No: 8291048/12\n"
            "Scheme: HDFC Balanced Advantage Fund - Regular Growth\n"
            "NAV as on 30/09/2026: ₹452.18\n"
            "Current Valuation: ₹1,35,654.00\n"
            "Statutory Note: Mutual Fund investments are subject to market risks, read all scheme related documents carefully.\n"
            "Website: www.hdfcfund.com | Email: cliser@hdfcfund.com | Toll-Free: 1800 3010 6767"
        ),
        "critical_fields_mock": [
            {
                "field_type": "MONETARY_AMOUNT",
                "raw_text": "₹1,35,654.00",
                "bbox": {"x": 360, "y": 480, "w": 200, "h": 36},
                "tamper_concern": "LOW",
                "finding": "Consistent typography, uniform rasterization, and correct baseline alignment"
            }
        ],
        "claims_mock": [],
        "identity_mock": {
            "claimed": "HDFC Asset Management Company Ltd",
            "email": "cliser@hdfcfund.com",
            "website": "www.hdfcfund.com"
        }
    }
}


def get_all_demo_scenarios() -> List[Dict[str, Any]]:
    """
    Returns summarized catalog of deterministic demo cases for UI picker.
    """
    catalog = []
    for k, s in DEMO_SCENARIOS.items():
        catalog.append({
            "id": s["id"],
            "title": s["title"],
            "category": s["category"],
            "filename": s["filename"],
            "document_type": s["document_type"],
            "persona": s["persona"],
            "claimed_entity": s["claimed_entity"],
            "preview_badge": s["preview_badge"]
        })
    return catalog


def render_demo_canvas(demo_id: str, output_path: str):
    """
    Renders a realistic visual document representing the demo scenario.
    Generates real embedded QR matrix for payment cases, authentic letterheads,
    and structured document text.
    """
    import qrcode
    from PIL import Image, ImageDraw, ImageFont

    scenario = DEMO_SCENARIOS.get(demo_id, DEMO_SCENARIOS["kavita_whatsapp_scam"])

    width, height = 1240, 1754
    canvas = Image.new("RGB", (width, height), color=(253, 253, 254))
    draw = ImageDraw.Draw(canvas)

    # Fonts
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 32)
        subtitle_font = ImageFont.truetype("arialbd.ttf", 22)
        body_font = ImageFont.truetype("arial.ttf", 20)
        bold_font = ImageFont.truetype("arialbd.ttf", 20)
        footer_font = ImageFont.truetype("ariali.ttf", 15)
    except Exception:
        title_font = ImageFont.load_default()
        subtitle_font = title_font
        body_font = title_font
        bold_font = title_font
        footer_font = title_font

    # Top brand bar
    if demo_id in ("sebi_nsdl_50k_80k_certificate", "kavita_whatsapp_scam"):
        banner_color = (220, 38, 38)
    elif demo_id == "traditional_altered_bank_slip":
        banner_color = (30, 58, 138)
    elif demo_id == "ai_erased_dividend_receipt":
        banner_color = (13, 148, 136)
    else:
        banner_color = (37, 99, 235)

    draw.rectangle([(0, 0), (width, 16)], fill=banner_color)

    # Demo Benchmark Safety Watermark Badge
    draw.rectangle([(width - 340, 24), (width - 60, 56)], fill=(254, 226, 226), outline=(239, 68, 68), width=1)
    draw.text((width - 325, 31), "DEMO SAMPLE / SANGYAN HACKATHON", fill=(185, 28, 28), font=footer_font)

    # Document Header
    y = 60
    draw.text((70, y), scenario["claimed_entity"].upper(), fill=(15, 23, 42), font=title_font)
    y += 45
    draw.text((70, y), scenario["document_type"], fill=(100, 116, 139), font=subtitle_font)
    y += 35
    draw.line([(70, y), (1170, y)], fill=(226, 232, 240), width=2)
    y += 40

    # Body lines
    lines = scenario["sample_text"].split("\n")[2:] # Skip entity and doc type as they're in header
    for line in lines:
        line = line.strip()
        if not line:
            y += 20
            continue

        if any(keyword in line.lower() for keyword in ["guaranteed", "sebi approved", "act now", "pay immediately", "amount in figures", "net dividend", "current valuation"]):
            draw.text((70, y), line, fill=(185, 28, 28) if "guaranteed" in line.lower() or "act now" in line.lower() else (15, 23, 42), font=bold_font)
        else:
            draw.text((70, y), line, fill=(51, 65, 85), font=body_font)
        y += 38

    # Embed QR Code if present
    qr_spec = scenario.get("qr_mock")
    if qr_spec:
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(qr_spec["raw_content"])
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            qr_img = qr_img.resize((240, 240))

            # Paste QR on right column
            qr_x = 850
            qr_y = 650
            canvas.paste(qr_img, (qr_x, qr_y))

            # Draw border and label
            draw.rectangle([(qr_x - 10, qr_y - 10), (qr_x + 250, qr_y + 280)], outline=(203, 213, 225), width=2)
            draw.text((qr_x + 15, qr_y + 250), "SCAN TO PAY VIA UPI", fill=(100, 116, 139), font=footer_font)
        except Exception:
            pass

    # Watermark / Footer
    draw.line([(70, 1660), (1170, 1660)], fill=(226, 232, 240), width=1)
    draw.text((70, 1680), f"Proofly Hackathon Benchmark Artifact: {scenario['filename']} | SANGYAN Hackathon Track A/C/E", fill=(148, 163, 184), font=footer_font)

    canvas.save(output_path, "JPEG", quality=95)
    return canvas
