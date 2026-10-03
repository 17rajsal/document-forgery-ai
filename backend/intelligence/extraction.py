"""Span-localized field and claim extraction; no external facts inferred."""
import re
from .schema import SensitiveField, Claim

FIELDS = {
    'amount': r'(?:₹|Rs\.?|INR)\s*\d[\d,]*(?:\.\d{1,2})?',
    'percentage': r'\b\d+(?:\.\d+)?\s*%',
    'date': r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
    'account': r'\b(?:account|a/c)\s*(?:no\.?|number)?\s*[:#-]?\s*([\dXx*][\dXx* -]{5,24}[\dXx*])',
    'phone': r'(?<!\w)(?:\+91[ -]?)?[6-9]\d{4}[ -]?\d{5}(?!\d)',
    'upi': r'\b[\w.+-]+@(?:upi|ybl|ibl|axl|paytm|ok\w+|sbi|hdfcbank|icici)\b',
    'registration': r'\b(?:IN[A-Z]{1,3}\d{6,12}|[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z])\b',
    'reference': r'\b(?:reference|ref|registration|licen[cs]e)\s*(?:no\.?|number|id)?\s*[:#-]\s*([\w/-]+)',
    'url': r'\b(?:https?://|www\.)[^\s<>]+',
    'email': r'\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b',
    'name': r'\b(?:name|beneficiary)\s*:\s*([^\n:]{2,70})',
    'entity': r'\b(?:issuer|broker|organisation|organization|company)\s*:\s*([^\n:]{2,80})',
}
CLAIMS = {
    'guaranteed_returns': r'\bguaranteed?\s+(?:\d+(?:\.\d+)?%\s+)?returns?\b|गारंटीड\s*रिटर्न',
    'zero_risk': r'\b(?:zero[- ]risk|risk[- ]free|no\s+risk)\b',
    'regulator_claim': r'\b(?:SEBI|RBI)\s*(?:approved|registered|regulated|authori[sz]ed)\b',
    'government_approval': r'\bgovernment\s*(?:approved|backed|authori[sz]ed)\b',
    'urgency': r'\b(?:act now|closing soon|last\s+\d+\s+(?:hours?|minutes?))\b',
    'fomo': r'\b(?:only\s+\d+\s+slots?\s+left|limited time offer|do not miss out)\b',
    'payment_pressure': r'\b(?:pay|transfer|deposit|send)\s+(?:now|immediately|urgently|today)\b|तुरंत\s*भुगतान',
    'fear': r'\b(?:account will be blocked|funds frozen|arrest warrant)\b',
    'licence_claim': r'\b(?:licen[cs]ed|registered)\s+(?:broker|adviser|advisor|company)\b',
    'impersonation_claim': r'\b(?:official representative of|on behalf of)\s+[^\n.,]{2,60}',
    'performance_claim': r'\b(?:returns? of|earned|profit of)\s+\d+(?:\.\d+)?\s*%',
}


def indexed_text(words):
    parts, spans, offset, previous = [], [], 0, None
    for word in words:
        value = word['text'].strip()
        if not value:
            continue
        line = word.get('line')
        sep = ('\n' if line != previous else ' ') if parts else ''
        parts.append(sep + value)
        offset += len(sep)
        spans.append((offset, offset + len(value), word))
        offset += len(value)
        previous = line
    return ''.join(parts), spans


def locate(spans, start, end):
    selected = [w for a, b, w in spans if a < end and b > start]
    if not selected:
        return None, 0.0
    box = (min(w['bbox'][0] for w in selected), min(w['bbox'][1] for w in selected),
           max(w['bbox'][2] for w in selected), max(w['bbox'][3] for w in selected))
    return box, sum(w['confidence'] for w in selected) / len(selected)


def extract(words, page):
    text, spans = indexed_text(words)
    fields, claims = [], []
    for kind, pattern in FIELDS.items():
        for m in re.finditer(pattern, text, re.I):
            group = 1 if m.lastindex else 0
            box, confidence = locate(spans, *m.span(group))
            fields.append(SensitiveField(type=kind, value=m.group(group).strip().rstrip('.,;)') if kind == 'url' else m.group(group).strip(), page=page,
                                         bbox=box, confidence=confidence))
    entity = next((f.value for f in fields if f.type == 'entity'), None)
    for category, pattern in CLAIMS.items():
        for m in re.finditer(pattern, text, re.I):
            # Keep educational / negated language out of assertion extraction.
            context = text[max(0, m.start()-70):m.start()].lower()
            if re.search(r'\b(?:not|never|avoid|beware|warning|no)\b[^.!?\n]*$', context):
                continue
            box, confidence = locate(spans, *m.span())
            claims.append(Claim(text=m.group(), category=category, page=page, bbox=box,
                                confidence=min(confidence, .85), extracted_entity=entity))
    return text, fields, claims
