"""Controlled synthetic edits; AI edits require imported provenance, never mislabeled blur."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from .training import split_for

FIELDS = {'amount':'Rs 98000','date':'12/10/2026','account':'9988776655',
          'url':'https://example.invalid/pay','phone':'9876543210','percentage':'28%',
          'registration':'INZ000000001','text':'Edited sample'}


def generate(source, output, bbox):
    image = Image.open(source).convert('RGB')
    x1,y1,x2,y2 = bbox
    if not (0 <= x1 < x2 <= image.width and 0 <= y1 < y2 <= image.height):
        raise ValueError('Edit box must fit the source')
    source_id=hashlib.sha256(Path(source).read_bytes()).hexdigest()
    folder=Path(output)/source_id
    folder.mkdir(parents=True,exist_ok=True)
    original=folder/'original.png';image.save(original)
    rows=[]
    specs=[('genuine',None),('traditional_edit','overlay'),('logo_replacement','logo'),
           ('qr_replacement','qr'),('inpainting','inpaint'),('recompressed_screenshot','jpeg'),
           ('low_resolution','resize')]+[(('date_replacement' if k=='date' else 'text_replacement' if k in {'text','url','registration'} else 'number_replacement'),k) for k in FIELDS]
    for index,(kind,operation) in enumerate(specs):
        edited=image.copy();mask=Image.new('L',image.size,0)
        if operation and operation not in {'jpeg','resize'}:
            ImageDraw.Draw(mask).rectangle((x1,y1,x2-1,y2-1),fill=255)
            draw=ImageDraw.Draw(edited)
            if operation=='inpaint':
                edited=Image.fromarray(cv2.inpaint(np.asarray(image),np.asarray(mask),3,cv2.INPAINT_TELEA))
            elif operation=='qr':
                import qrcode
                patch=qrcode.make('upi://pay?pa=synthetic@upi&pn=Test').convert('RGB').resize((x2-x1,y2-y1),Image.Resampling.NEAREST)
                edited.paste(patch,(x1,y1))
            else:
                patch=Image.new('RGB',(x2-x1,y2-y1),'white')
                patch_draw=ImageDraw.Draw(patch)
                if operation=='logo':
                    patch_draw.ellipse((2,2,min(25,x2-x1-1),min(25,y2-y1-1)),fill='navy')
                else:
                    patch_draw.text((2,2),FIELDS.get(operation,'SYNTHETIC'),fill='black')
                edited.paste(patch,(x1,y1))
        elif operation=='resize':
            edited=edited.resize((max(1,image.width//3),max(1,image.height//3))).resize(image.size)
        name=f'{index:02d}_{kind}'
        target=folder/(name+('.jpg' if operation=='jpeg' else '.png'))
        edited.save(target,quality=40) if operation=='jpeg' else edited.save(target)
        mask_path=folder/(name+'_mask.png');mask.save(mask_path)
        metadata={'source_id':source_id,'split':split_for(source_id),'manipulation':kind,
                  'field':operation,'original':str(original.resolve()),'filename':str(target.resolve()),
                  'mask':str(mask_path.resolve()),'label':int(operation not in {None,'jpeg','resize'}),
                  'method':'OpenCV Telea' if operation=='inpaint' else 'controlled synthetic',
                  'localisation_applicable':operation not in {None,'jpeg','resize'},
                  'bbox':bbox,'ai_generated':False}
        (folder/(name+'.json')).write_text(json.dumps(metadata,indent=2),encoding='utf-8')
        rows.append(metadata)
    (folder/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    return rows


def import_ai_edit(original, edited, mask, output, kind, provenance):
    if kind not in {'ai_erase','generative_fill'} or not provenance.strip():
        raise ValueError('AI imports require kind and generation provenance')
    images=[Image.open(p) for p in (original,edited,mask)]
    if len({im.size for im in images}) != 1: raise ValueError('Images and mask must align')
    source_id=hashlib.sha256(Path(original).read_bytes()).hexdigest()
    folder=Path(output)/source_id/kind;folder.mkdir(parents=True,exist_ok=True)
    for image,name in zip(images,('original','edited','mask')):
        image.save(folder/(name+'.png'))
    row={'source_id':source_id,'split':split_for(source_id),'manipulation':kind,'label':1,
         'original':str((folder/'original.png').resolve()),'filename':str((folder/'edited.png').resolve()),
         'mask':str((folder/'mask.png').resolve()),'provenance':provenance,'ai_generated':True}
    (folder/'metadata.json').write_text(json.dumps(row,indent=2),encoding='utf-8')
    return row


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--bbox',type=int,nargs=4,required=True)
    args=parser.parse_args()
    print(json.dumps(generate(args.source,args.output,args.bbox),indent=2))
