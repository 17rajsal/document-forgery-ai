"""Conservative local heuristics plus existing ELA/noise/copy-move detectors."""
from io import BytesIO
import cv2
import numpy as np
from PIL import Image, ImageChops
from .schema import Finding


def local_signals(image, page):
    gray = np.asarray(image.convert('L'), dtype=np.float32)
    residual = gray - cv2.GaussianBlur(gray, (5, 5), 0)
    buffer = BytesIO()
    image.convert('RGB').save(buffer, format='JPEG', quality=90)
    buffer.seek(0)
    with Image.open(buffer) as compressed:
        error = np.asarray(ImageChops.difference(image.convert('RGB'), compressed.convert('RGB')), dtype=float).mean(2)
    tiles = []
    for y in range(0, image.height-63, 64):
        for x in range(0, image.width-63, 64):
            patch = gray[y:y+64, x:x+64]
            # Compare low-edge background regions, not text against blank paper.
            edge = float((np.abs(cv2.Laplacian(patch, cv2.CV_32F)) > 20).mean())
            tiles.append((x, y, float(residual[y:y+64,x:x+64].std()),
                          float(error[y:y+64,x:x+64].mean()), edge, float(patch.mean())))
    findings = []
    for x, y, noise, ela, edge, mean in tiles:
        peers = [t for t in tiles if 0 < max(abs(t[0]-x),abs(t[1]-y)) <= 128
                 and abs(t[4]-edge) < .035 and abs(t[5]-mean) < 18]
        if len(peers) < 4:
            continue
        typical_noise = float(np.median([t[2] for t in peers]))
        typical_ela = float(np.median([t[3] for t in peers]))
        kind = None
        if edge < .025 and typical_noise > 1.8 and noise < typical_noise*.22:
            kind = 'possible_reconstructed_background'
            explanation = 'Background residual is unusually smooth relative to nearby similar patches. Denoising, blank paper, erasure or inpainting can cause this; AI origin cannot be determined.'
        elif noise > max(3.0, typical_noise*3.5) and ela > max(3.0, typical_ela*2.8):
            kind = 'local_noise_compression_inconsistency'
            explanation = 'Local noise and JPEG recompression residual differ from similar neighboring patches. Overlay, resampling or ordinary image processing may explain this.'
        if kind:
            findings.append(Finding(type=kind, page=page, bbox=(x,y,x+64,y+64), confidence=.55, explanation=explanation))
    return findings[:40]


def field_signals(image, fields, words, page):
    findings = []
    gray = np.asarray(image.convert('L'))
    for field in fields:
        if not field.bbox or field.confidence < .5:
            continue
        x1,y1,x2,y2 = field.bbox
        nearby = [w for w in words if abs(w['bbox'][3]-y2) < max(10,y2-y1)
                  and (w['bbox'][2] < x1 or w['bbox'][0] > x2)]
        if len(nearby) < 3:
            continue
        heights = [w['bbox'][3]-w['bbox'][1] for w in nearby]
        height = y2-y1
        baseline = float(np.median([w['bbox'][3] for w in nearby]))
        if height > np.median(heights)*1.7 and abs(y2-baseline) > max(4, height*.2):
            field.concern = 'Text height and baseline differ from neighboring text; formatting may explain this.'
            findings.append(Finding(type='sensitive_field_typography',page=page,bbox=field.bbox,
                                    confidence=.5,explanation=field.concern))
    return findings


def run_forensics(image, page):
    from forgery_detector import perform_ela, analyze_noise_inconsistency, detect_copy_move
    findings, diagnostics = [], {}
    for name, detector in [('ela',perform_ela), ('noise',analyze_noise_inconsistency), ('copy_move',detect_copy_move)]:
        try:
            result = detector(image)
            diagnostics[name] = {k:v for k,v in result.items() if not k.endswith('_image')}
            flagged = result.get('status') == 'HIGH_ANOMALY' or result.get('anomaly_detected') or result.get('detected')
            if flagged:
                findings.append(Finding(type=name,page=page,bbox=None,confidence=.55,
                    explanation=f'{name.replace("_", " ")} heuristic indicates a page-level anomaly. Compression, repeated layout or scanning can also cause this signal.'))
        except Exception as exc:
            diagnostics[name] = {'available':False,'reason':type(exc).__name__}
    try:
        findings.extend(local_signals(image,page))
        diagnostics['local'] = {'available':True,'method':'neighbor-matched residual heuristic; not an AI classifier'}
    except Exception as exc:
        diagnostics['local'] = {'available':False,'reason':type(exc).__name__}
    return findings, diagnostics


def semantic_signals(fields):
    """Limited contradictions supported by the extracted value itself."""
    from datetime import date
    import re
    findings = []
    for field in fields:
        if field.type != 'date' or field.confidence < .7:
            continue
        parts = re.split(r'[-/]', field.value)
        if len(parts) != 3 or len(parts[-1]) == 2:
            continue
        a,b,c = map(int, parts)
        try:
            if len(parts[0]) == 4:
                date(a,b,c)
            else:
                try:
                    date(c,b,a)
                except ValueError:
                    date(c,a,b)
        except ValueError:
            field.concern = 'Extracted date is not a valid calendar date; confirm against the image in case of OCR error.'
            findings.append(Finding(type='semantic_date_inconsistency',page=field.page,bbox=field.bbox,
                                    confidence=min(field.confidence,.8),explanation=field.concern))
    return findings
