"""Audited source-grouped interpretable baseline. Does not replace the CNN."""
import argparse
import csv
import json
from io import BytesIO
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from dataset_manager import create_grouped_splits
from .training import audit, evaluate, metrics

FEATURES=['gray_std','laplacian_std','residual_std','edge_fraction','jpeg_error_mean','jpeg_error_std']


def features(path):
    with Image.open(path) as source:
        image=source.convert('RGB');image.thumbnail((512,512))
    gray=np.asarray(image.convert('L'),dtype=np.float32)
    residual=gray-cv2.GaussianBlur(gray,(5,5),0)
    lap=cv2.Laplacian(gray,cv2.CV_32F)
    buffer=BytesIO();image.save(buffer,format='JPEG',quality=90);buffer.seek(0)
    with Image.open(buffer) as jpg:
        diff=np.abs(np.asarray(image,dtype=float)-np.asarray(jpg,dtype=float))
    return [float(gray.std()),float(lap.std()),float(residual.std()),float((np.abs(lap)>20).mean()),float(diff.mean()),float(diff.std())]


def train(manifest,root,output):
    with Path(manifest).open(encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
    before=audit(rows,root)
    # Build a separate split manifest; never rearrange existing files or overwrite CNN weights.
    rows=[r for partition in create_grouped_splits(rows) for r in partition]
    for row in rows:
        candidate=Path(root)/'docs'/row['filename']
        if not candidate.is_file():
            raise ValueError('Baseline requires originals under dataset/docs; missing '+row['filename'])
        row['filename']=str(candidate.resolve())
    after=audit(rows,root)
    if not after['safe_to_train']: raise ValueError('Repaired manifest still fails audit')
    x=np.asarray([features(r['filename']) for r in rows])
    y=np.asarray([int(r['label']=='forged') for r in rows])
    train_idx=np.array([r['split']=='train' for r in rows])
    val_idx=np.array([r['split']=='validation' for r in rows])
    test_idx=np.array([r['split']=='test' for r in rows])
    if any(len(set(y[idx]))<2 for idx in (train_idx,val_idx,test_idx)):
        raise ValueError('Each split needs both labels')
    mean=x[train_idx].mean(0);scale=x[train_idx].std(0);scale[scale<1e-8]=1
    x=np.column_stack(((x-mean)/scale,np.ones(len(x))))
    weights=np.zeros(x.shape[1])
    for _ in range(1200):
        probabilities=1/(1+np.exp(-np.clip(x[train_idx]@weights,-30,30)))
        gradient=x[train_idx].T@(probabilities-y[train_idx])/train_idx.sum()
        gradient[:-1]+=.01*weights[:-1]
        weights-=.08*gradient
    scores=1/(1+np.exp(-np.clip(x@weights,-30,30)))
    validation=[{'label':int(y[i]),'score':float(scores[i])} for i in np.where(val_idx)[0]]
    # Select on validation only; test data is evaluated once with the frozen threshold.
    threshold=max(np.linspace(.1,.9,81),key=lambda t:(metrics(validation,t)['f1'] or 0,-float(t)))
    predictions=[{'label':int(y[i]),'score':float(scores[i]),'manipulation':rows[i].get('manipulation','unspecified')}
                 for i in np.where(test_idx)[0]]
    result={'architecture':'L2 logistic regression over six image summary features',
            'source_audit_before':before,'source_audit_after':after,
            'split_counts':{s:sum(r['split']==s for r in rows) for s in ('train','validation','test')},
            'threshold':float(threshold),'test':metrics(predictions,float(threshold)),
            'per_manipulation':{k:metrics([r for r in predictions if r['manipulation']==k],float(threshold))
                                for k in sorted({r['manipulation'] for r in predictions})},
            'limitations':['Synthetic repository corpus only; not independent real-world validation.',
                           'Manipulation subtypes and localization masks absent in legacy manifest.',
                           'Not enabled in API fusion. Scores are not calibrated probabilities.']}
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    model={'features':FEATURES,'mean':mean.tolist(),'scale':scale.tolist(),'weights':weights.tolist(),'threshold':float(threshold)}
    (output/'baseline_model.json').write_text(json.dumps(model,indent=2))
    (output/'evaluation.json').write_text(json.dumps(result,indent=2))
    (output/'test_predictions.json').write_text(json.dumps(predictions,indent=2))
    with (output/'source_safe_manifest.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({k:result[k] for k in ('split_counts','threshold','test')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('manifest');parser.add_argument('root');parser.add_argument('output')
    args=parser.parse_args();train(args.manifest,args.root,args.output)
