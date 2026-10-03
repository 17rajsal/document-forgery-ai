"""Source-level leakage audit, deterministic splitting and honest evaluation."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

MANIPULATIONS = ('genuine','traditional_edit','text_replacement','number_replacement',
    'date_replacement','qr_replacement','logo_replacement','ai_erase','inpainting',
    'generative_fill','recompressed_screenshot','low_resolution')


def split_for(source_id):
    bucket = int(hashlib.sha256(source_id.encode()).hexdigest()[:8],16) % 100
    return 'train' if bucket < 60 else 'validation' if bucket < 80 else 'test'


def audit(records, root=None):
    groups, hashes, missing, unknown = defaultdict(set),defaultdict(set),[],[]
    for row in records:
        source = row.get('source_id') or row.get('base_id')
        if not source:
            unknown.append(row.get('filename','?'))
            continue
        groups[source].add(row.get('split',''))
        if root:
            candidates = [Path(root)/row['filename'],Path(root)/'docs'/row['filename'],
                Path(root)/row.get('split','')/row.get('label','')/row['filename']]
            path = next((p for p in candidates if p.is_file()),None)
            if path:
                hashes[hashlib.sha256(path.read_bytes()).hexdigest()].add(row.get('split',''))
            else: missing.append(row['filename'])
    leaks = [k for k,v in groups.items() if len(v)>1]
    duplicate_leaks = sum(len(v)>1 for v in hashes.values())
    counts = Counter(r.get('manipulation','unspecified') for r in records)
    invalid_splits = sum(r.get('split') not in {'train','validation','test'} for r in records)
    return {'records':len(records),'source_groups':len(groups),'leaking_sources':leaks,
            'cross_split_duplicate_hashes':duplicate_leaks,'missing_files':missing,
            'missing_source_ids':unknown,'invalid_splits':invalid_splits,
            'manipulation_counts':dict(counts),
            'missing_manipulation_labels':[m for m in MANIPULATIONS if not counts[m]],
            'safe_to_train':bool(records) and not (leaks or duplicate_leaks or missing or unknown or invalid_splits)}


def metrics(rows, threshold=.5):
    # Input rows: label (0/1), score [0,1], manipulation; optional mask_iou.
    if not rows: return {'samples':0,'precision':None,'recall':None,'f1':None,'false_positive_rate':None,'roc_auc':None}
    for r in rows:
        if r['label'] not in (0,1) or not 0 <= r['score'] <= 1: raise ValueError('Invalid prediction')
    tp=sum(r['label']==1 and r['score']>=threshold for r in rows)
    fp=sum(r['label']==0 and r['score']>=threshold for r in rows)
    tn=sum(r['label']==0 and r['score']<threshold for r in rows)
    fn=sum(r['label']==1 and r['score']<threshold for r in rows)
    div=lambda a,b: a/b if b else None
    positive=[r['score'] for r in rows if r['label']==1]
    negative=[r['score'] for r in rows if r['label']==0]
    auc=div(sum((p>n)+.5*(p==n) for p in positive for n in negative),len(positive)*len(negative))
    ious=[r['mask_iou'] for r in rows if r.get('mask_iou') is not None]
    return {'samples':len(rows),'precision':div(tp,tp+fp),'recall':div(tp,tp+fn),
            'f1':div(2*tp,2*tp+fp+fn),'false_positive_rate':div(fp,fp+tn),'roc_auc':auc,
            'localisation_iou':sum(ious)/len(ious) if ious else None,
            'confusion':{'tp':tp,'fp':fp,'tn':tn,'fn':fn}}


def localisation_iou(predicted, expected):
    import numpy as np
    predicted, expected = np.asarray(predicted, dtype=bool), np.asarray(expected, dtype=bool)
    if predicted.shape != expected.shape:
        raise ValueError('Localization masks must have identical shapes')
    union = np.logical_or(predicted, expected).sum()
    return float(np.logical_and(predicted, expected).sum()/union) if union else None


def evaluate(rows):
    return {'overall':metrics(rows),'per_manipulation':{
        kind:metrics([r for r in rows if r.get('manipulation')==kind])
        for kind in sorted({r.get('manipulation','unspecified') for r in rows})}}


def audit_image_folders(root, samples):
    """Guard ImageFolder training against unmanifested files and source leakage."""
    manifest = Path(root) / 'manifest.csv'
    if not manifest.is_file():
        return {'safe_to_train': False, 'reason': 'Source manifest missing'}
    with manifest.open(encoding='utf-8-sig', newline='') as f:
        records = list(csv.DictReader(f))
    by_name = {r['filename']: r for r in records}
    actual, unknown = [], []
    for split, items in samples.items():
        for filename, _ in items:
            name = Path(filename).name
            if name not in by_name:
                unknown.append(name)
            else:
                actual.append({**by_name[name], 'filename': str(Path(filename).resolve()), 'split': split})
    result = audit(actual, root)
    result['unmanifested_images'] = len(unknown)
    result['safe_to_train'] = result['safe_to_train'] and not unknown
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--root',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    with args.manifest.open(encoding='utf-8-sig',newline='') as f:
        records=list(csv.DictReader(f))
    result=audit(records,args.root)
    output=json.dumps(result,indent=2)
    if args.output: args.output.write_text(output,encoding='utf-8')
    print(output)
