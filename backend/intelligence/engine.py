"""Bounded multipage inference with independently failing components."""
import os
import hashlib
import uuid
from pathlib import Path
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageSequence, ImageOps
from .schema import Analysis, Document, Assessment, Explanation
from .extraction import extract
from .destinations import inspect, identities
from .evidence import EvidenceStore
from .forensics import run_forensics, field_signals, semantic_signals

MAX_PAGES = 20
MAX_PIXELS = 12_000_000


def pages(path):
    if Path(path).suffix.lower() == '.pdf':
        import pypdfium2 as pdfium
        with pdfium.PdfDocument(path) as pdf:
            if not 0 < len(pdf) <= MAX_PAGES:
                raise ValueError('PDF page limit is 20')
            for index in range(len(pdf)):
                page = pdf[index]
                try:
                    w,h = page.get_size()
                    if w*h*4 > MAX_PIXELS:
                        raise ValueError('Rendered page exceeds pixel limit')
                    bitmap = page.render(scale=2)
                    try:
                        yield bitmap.to_pil().convert('RGB').copy()
                    finally:
                        bitmap.close()
                finally:
                    page.close()
    else:
        with Image.open(path) as image:
            if getattr(image,'n_frames',1) > MAX_PAGES:
                raise ValueError('Image page limit is 20')
            for frame in ImageSequence.Iterator(image):
                if frame.width*frame.height > MAX_PIXELS:
                    raise ValueError('Image exceeds pixel limit')
                yield ImageOps.exif_transpose(frame).convert('RGB')


def ocr(image):
    candidates = []
    for psm in (6, 3):
        try:
            data = pytesseract.image_to_data(image, config=f'--psm {psm}',
                lang=os.getenv('PROOFLY_OCR_LANG','eng'), output_type=pytesseract.Output.DICT, timeout=25)
            words = []
            for i, text in enumerate(data['text']):
                if not text.strip():
                    continue
                x,y,w,h = (int(data[k][i]) for k in ('left','top','width','height'))
                if w <= 0 or h <= 0:
                    continue
                words.append({'text':text, 'confidence':max(0,min(1,float(data['conf'][i])/100)),
                              'bbox':(x,y,x+w,y+h),
                              'line':(data['block_num'][i],data['par_num'][i],data['line_num'][i])})
            confidence = sum(w['confidence'] for w in words)/max(1,len(words))
            candidates.append((words,confidence))
            if confidence >= .8 and len(words) >= 8:
                break
        except Exception:
            continue
    if not candidates:
        return [], {'available':False,'confidence':0,'reason':'OCR unavailable or timed out'}
    words, confidence = max(candidates, key=lambda c: c[1]*min(len(c[0]),20))
    return words, {'available':True,'confidence':confidence,'words':words}


def fuse(findings, claims, urls, identities, coverage):
    # Correlated image detectors form one family. Repeated phrases never multiply risk.
    families = set()
    if findings: families.add('visual')
    if any(c.confidence >= .5 for c in claims): families.add('language')
    if any(u.concerns for u in urls): families.add('destination')
    if any(i.inconsistencies for i in identities): families.add('identity')
    if any(c.verification_status == 'conflicting' for c in claims): families.add('evidence')
    level = 'HIGH' if len(families) >= 3 else 'MODERATE' if families or coverage < 1 else 'LOW'
    summary = f'{level.title()} verification concern across {len(families)} signal families. '
    summary += 'These signals do not establish fraud or authenticity.'
    if coverage < 1: summary += ' Analysis is incomplete; review unavailable checks.'
    return Assessment(level=level,summary=summary,confidence=round(.65*coverage,3)), sorted(families)


def analyze(path, filename):
    findings, fields, claims, qr, urls, technical = [], [], [], [], [], []
    evidence_store = EvidenceStore(os.getenv('PROOFLY_EVIDENCE_CORPUS'))
    for page_number, image in enumerate(pages(path),1):
        words, ocr_details = ocr(image)
        text, page_fields, page_claims = extract(words,page_number)
        page_findings, diagnostics = run_forensics(image,page_number)
        page_findings.extend(semantic_signals(page_fields))
        try:
            page_findings.extend(field_signals(image,page_fields,words,page_number))
            diagnostics['field_typography'] = {'available':True}
        except Exception as exc:
            diagnostics['field_typography'] = {'available':False,'reason':type(exc).__name__}
        for field in page_fields:
            if field.type == 'url': urls.append(inspect(field.value,page_number,field.bbox,field.confidence))
        try:
            success, decoded, points, _ = cv2.QRCodeDetector().detectAndDecodeMulti(np.asarray(image))
            if success:
                for value, polygon in zip(decoded,points):
                    if not value: continue
                    x1,y1 = np.floor(polygon.min(axis=0)).astype(int)
                    x2,y2 = np.ceil(polygon.max(axis=0)).astype(int)
                    box = (max(0,int(x1)),max(0,int(y1)),min(image.width,int(x2)),min(image.height,int(y2)))
                    qr.append(inspect(value,page_number,box))
            diagnostics['qr'] = {'available':True}
        except Exception as exc:
            diagnostics['qr'] = {'available':False,'reason':type(exc).__name__}
        findings.extend(page_findings)
        fields.extend(page_fields)
        claims.extend(evidence_store.verify(c) for c in page_claims)
        technical.append({'page':page_number,'width':image.width,'height':image.height,
                          'text':text,'ocr':ocr_details,'detectors':diagnostics})
    if not technical: raise ValueError('No readable pages')
    entity_map = identities(fields,urls+qr)
    checks = [p['ocr']['available'] and p['ocr']['confidence'] > 0 for p in technical]
    checks.extend(d.get('available',True) for p in technical for d in p['detectors'].values())
    coverage = sum(checks)/len(checks)
    assessment, families = fuse(findings,claims,urls+qr,entity_map,coverage)
    hi_level = {'LOW':'कम','MODERATE':'मध्यम','HIGH':'उच्च'}[assessment.level]
    return Analysis(document=Document(id=uuid.uuid4().hex,filename=filename,pages=len(technical)),
        assessment=assessment,forensics=findings,sensitive_fields=fields,claims=claims,qr_codes=qr,
        urls=urls,identities=entity_map,evidence=[e for c in claims for e in c.evidence],
        safe_actions=['Verify the issuer using independently obtained contact details.',
                      'Confirm payment identifiers before sending money.',
                      'Do not follow document links until their destination is independently checked.'],
        simple_explanation=Explanation(en=assessment.summary,
            hi=f'सत्यापन की चिंता: {hi_level}। ये संकेत धोखाधड़ी या प्रामाणिकता का प्रमाण नहीं हैं। जारीकर्ता और भुगतान विवरण स्वतंत्र रूप से जाँचें।' + (' जाँच अधूरी है।' if coverage < 1 else '')),
        technical_details={'pages':technical,'coverage':coverage,'signal_families':families,
            'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            'evidence_lookup_available':evidence_store.available,
            'confidence_semantics':'uncalibrated heuristic strength, not fraud probability',
            'limitations':['AI origin and editing tool cannot be inferred from smoothing.',
                          'Rasterized PDF signals include rendering artifacts.',
                          'No logo reference matching or ownership registry is configured.',
                          'Legacy ML checkpoint is excluded from fusion pending leakage-free validation.']})
