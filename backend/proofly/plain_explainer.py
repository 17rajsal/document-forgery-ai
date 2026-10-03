"""
Proofly Plain-Language Explainer & Bharat-First Bilingual Engine
Translates technical forensic findings into accessible, jargon-free explanations,
natural Hindi / Hinglish narratives, voice synthesis scripts, and actionable safe steps.
"""

from typing import Dict, Any, List


def generate_plain_explanations(
    assessment: Dict[str, Any],
    claims: List[Dict[str, Any]],
    financial_fields: Dict[str, Any],
    identity_res: Dict[str, Any],
    qr_res: List[Dict[str, Any]],
    ai_inpainting_res: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Creates simplified English and Hindi explanations, a spoken audio script,
    and investor safety recommendations.
    """
    concern = assessment.get("concern_level", "LOW")

    # 1. English Simplified Narrative
    simple_en_points = []
    if ai_inpainting_res.get("inpainting_detected"):
        simple_en_points.append(
            "Certain sections of this document look smoothed out or digitally reconstructed, as if text or numbers were erased and rewritten."
        )

    if financial_fields.get("semantic_contradictions"):
        simple_en_points.append(
            "The numeric amount does not match the amount written in words elsewhere on the page."
        )
    elif financial_fields.get("tampered_fields"):
        simple_en_points.append(
            "The font or background around key financial figures (like the amount or return percentage) looks inconsistent with the rest of the text."
        )

    for c in claims[:2]:
        if c.get("category") == "GUARANTEED_RETURN_CLAIMS":
            simple_en_points.append(
                f"The document promises '{c.get('exact_text')}'. In India, real stock market investments are never allowed to guarantee fixed returns."
            )
        elif c.get("category") == "REGULATOR_AUTHORITY_CLAIMS":
            simple_en_points.append(
                f"It claims to be '{c.get('exact_text')}'. Regulators like SEBI oversee markets, but never sponsor or guarantee individual investment schemes."
            )
        elif c.get("category") == "URGENCY_FOMO":
            simple_en_points.append(
                f"It pushes urgent action ('{c.get('exact_text')}'). Scammers often use time pressure so you send money before checking the facts."
            )

    for mm in identity_res.get("mismatches", [])[:2]:
        if mm.get("code") == "PUBLIC_EMAIL_FOR_CORPORATE_ENTITY":
            simple_en_points.append(
                "The document claims to be from a financial firm, but lists a personal email address (like Gmail) instead of an official company email."
            )
        elif mm.get("code") == "UPI_RECIPIENT_IDENTITY_MISMATCH":
            simple_en_points.append(
                "The payment or QR code asks you to send money to a personal individual's account, not a registered company bank account."
            )

    if not simple_en_points:
        simple_en_summary = (
            "We did not detect any obvious signs of digital editing or suspicious scam language in this document. "
            "However, always make sure you know who you are dealing with before transferring any money."
        )
    else:
        simple_en_summary = " ".join(simple_en_points)

    # 2. Hindi / Hinglish Simplified Narrative (Accessible to Tier-2/Tier-3 investors)
    simple_hi_points = []
    if ai_inpainting_res.get("inpainting_detected"):
        simple_hi_points.append(
            "Is document ke kuch hisso mein digital safai ya editing ke nishaan mile hain, jaise koi number ya naam mita kar dobara likha gaya ho."
        )

    if financial_fields.get("semantic_contradictions"):
        simple_hi_points.append(
            "Document mein likhi hui amount (ankon mein) aur shabdon (words) mein likhi hui rashi aapas mein match nahi kar rahi hai."
        )
    elif financial_fields.get("tampered_fields"):
        simple_hi_points.append(
            "Zaruri rakam (amount) ya returns ke aas-paas ka font aur background baaki document se alag dikhta hai."
        )

    for c in claims[:2]:
        if c.get("category") == "GUARANTEED_RETURN_CLAIMS":
            simple_hi_points.append(
                f"Document mein '{c.get('exact_text')}' ka vada kiya gaya hai. Bharat mein SEBI ke niyam anusaar share market mein kabhi pakka ya guaranteed return nahi diya ja sakta."
            )
        elif c.get("category") == "REGULATOR_AUTHORITY_CLAIMS":
            simple_hi_points.append(
                f"Yahan '{c.get('exact_text')}' ka daawa hai. SEBI ya Sarkar niyam banate hain, lekin kisi private scheme ki guarantee kabhi nahi dete."
            )
        elif c.get("category") == "URGENCY_FOMO":
            simple_hi_points.append(
                "Jaldbaazi mein paise bhejne ka dabav banaya ja raha hai, taaki aap kisi se salah na le sakein."
            )

    for mm in identity_res.get("mismatches", [])[:2]:
        if mm.get("code") == "PUBLIC_EMAIL_FOR_CORPORATE_ENTITY":
            simple_hi_points.append(
                "Badi company ka naam likha hai, par contact ke liye aam Gmail address diya gaya hai jo suspicious hai."
            )
        elif mm.get("code") == "UPI_RECIPIENT_IDENTITY_MISMATCH":
            simple_hi_points.append(
                "QR code ya payment kisi anjaan vyakti ke personal account par bhejne ko keh raha hai, kisi registered company ko nahi."
            )

    if not simple_hi_points:
        simple_hi_summary = (
            "Is document mein koi badi digital chhed-chhad ya dhokhadhadi ke sanket nahi mile hain. "
            "Phir bhi kisi bhi anjaan vyakti ko paise transfer karne se pehle achhi tarah janch kar lein."
        )
    else:
        simple_hi_summary = " ".join(simple_hi_points)

    # 3. Voice Scripts (Short, calm, uncertainty communicated)
    if concern == "HIGH":
        voice_script_en = (
            "Notice: Multiple verification concerns were detected in this document. "
            "Key financial amounts show potential signs of alteration, and the document promises guaranteed returns. "
            "The payment QR code points to an individual account. "
            "Please pause and verify the organization through official channels before sending any money."
        )
        voice_script_hi = (
            "Dhyan dein: Is document mein kai zaruri cheezein sandehpurna mili hain. "
            "Rakam ke paas editing ke sanket hain aur guaranteed return ka daawa kiya gaya hai. "
            "QR code bhi kisi personal account par paise mang raha hai. "
            "Paise bhejne se pehle official website se company ki janch zaroor karein."
        )
    elif concern == "MODERATE":
        voice_script_en = (
            "Notice: Some elements in this document warrant caution. "
            "There are minor visual inconsistencies or unverified claims. "
            "We recommend verifying the issuer's credentials directly before taking financial steps."
        )
        voice_script_hi = (
            "Dhyan dein: Is document ke kuch claims aur details ko dhyan se janchne ki zaroorat hai. "
            "Koi bhi paisa lagane se pehle authorised broker ya official source se confirm karein."
        )
    else:
        voice_script_en = (
            "Notice: No major digital tampering or high-risk claims were flagged in this document. "
            "Always follow safe investing practices."
        )
        voice_script_hi = (
            "Is document mein koi bada jhol nahi dikha hai. Hamesha savdhani se nivesh karein."
        )

    # 4. Safe Next Steps (Actionable & Non-Advisory)
    safe_steps = [
        {
            "step": 1,
            "title": "Pause Before Transferring Any Money",
            "title_hi": "Paisa transfer karne se pehle thode der rukein",
            "description": "Never send money under time pressure or artificial countdowns.",
            "description_hi": "Kisi ke dabav ya jaldi offer khatam hone ke daawe mein aakar turant paise na bhejein."
        },
        {
            "step": 2,
            "title": "Verify Organization via Official Directory",
            "title_hi": "Company ko official SEBI / RBI directory mein check karein",
            "description": "Search the intermediary on sebi.gov.in or sachet.rbi.org.in. Do not use phone numbers printed on the document.",
            "description_hi": "Document par likhe number par bharosa na karein. Official website sebi.gov.in par jakar registration verify karein."
        },
        {
            "step": 3,
            "title": "Inspect Bank & UPI Payee Name",
            "title_hi": "UPI payee ka asli naam verify karein",
            "description": "Legitimate investment firms receive funds in corporate escrow accounts, never personal UPI handles.",
            "description_hi": "Investment ka paisa kabhi kisi vyakti ke personal UPI ya aam bank account mein nahi jata."
        },
        {
            "step": 4,
            "title": "Preserve Document & Report Suspicious Activity",
            "title_hi": "Document sambhal kar rakhein aur helpline par report karein",
            "description": "Save original screenshots and chat exports. If defrauded, immediately dial the National Cybercrime Helpline at 1930.",
            "description_hi": "Original file aur chat ka screenshot rakhein. Dhokha hone par turant Cybercrime Helpline 1930 par call karein."
        }
    ]

    return {
        "simple_explanation_en": simple_en_summary,
        "simple_explanation_hi": simple_hi_summary,
        "voice_script_en": voice_script_en,
        "voice_script_hi": voice_script_hi,
        "safe_steps": safe_steps
    }
