"""Regression tests for localization, honest uncertainty, leakage and API storage."""
import asyncio
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
from pydantic import ValidationError
import sys
sys.path.insert(0, str(Path(__file__).parent))
from intelligence.schema import Finding, Claim, Evidence
from intelligence.extraction import extract
from intelligence.destinations import inspect, identities
from intelligence.evidence import EvidenceStore
from intelligence.engine import analyze, fuse
from intelligence.training import audit, metrics
from dataset_manager import create_grouped_splits


def words(text):
    return [{'text':token,'bbox':(i*90,10,i*90+80,30),'confidence':.9,'line':(1,1,1)}
            for i,token in enumerate(text.split())]


class IntelligenceTests(unittest.TestCase):
    def test_span_boxes_use_actual_occurrence(self):
        _,fields,claims=extract(words('Rs 100 Rs 200 guaranteed returns'),2)
        amounts=[f for f in fields if f.type=='amount']
        self.assertEqual(amounts[0].bbox,(0,10,170,30))
        self.assertEqual(amounts[1].bbox,(180,10,350,30))
        self.assertEqual(claims[0].bbox,(360,10,530,30))
        self.assertEqual(claims[0].page,2)

    def test_negation_and_repeated_claims(self):
        self.assertEqual(extract(words('Beware of guaranteed returns'),1)[2],[])
        claims=extract(words('guaranteed returns '*8),1)[2]
        result,_=fuse([],claims,[],[],1)
        self.assertEqual(result.level,'MODERATE')

    def test_schema_rejects_invalid_geometry(self):
        with self.assertRaises(ValidationError):
            Finding(type='test',page=0,bbox=(4,2,1,8),confidence=1.2,explanation='test')

    def test_passive_url_parsing(self):
        self.assertIn('Shortened',inspect('https://bit.ly/test',1).concerns[0])
        self.assertTrue(inspect('https://trusted.example@evil.invalid',1).concerns)
        self.assertEqual(inspect('upi://pay?pa=test%40upi',1).payment_identifier,'test@upi')
        self.assertTrue(inspect('javascript:alert(1)',1).concerns)
        self.assertTrue(inspect('https://[invalid',1).concerns)

    def test_lookup_unavailable_never_fabricates(self):
        claim=Claim(text='guaranteed returns',category='guaranteed_returns',page=1,confidence=.8)
        result=EvidenceStore('/missing/file').verify(claim)
        self.assertEqual(result.verification_status,'unable_to_verify')
        self.assertEqual(result.evidence,[])

    def test_evidence_does_not_implicitly_load_adjacent_corpus(self):
        with patch('intelligence.evidence.Path.is_file',return_value=True):
            store=EvidenceStore()
        self.assertFalse(store.available)
        self.assertEqual(store.records,[])

    def test_lookup_binds_exact_entity_and_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'corpus.json'
            path.write_text(json.dumps([{'claim_text':'registered broker','evidence':{
                'source_url':'https://example.org/record','title':'Fixture only','retrieved_at':'2026-10-03',
                'excerpt':'Synthetic test fixture','entity':'Example','relation':'supported'}}]))
            claim=Claim(text='registered broker',category='licence_claim',page=1,confidence=.8,extracted_entity='Other')
            self.assertEqual(EvidenceStore(path).verify(claim).verification_status,'not_corroborated')
            claim.extracted_entity='Example'
            self.assertEqual(EvidenceStore(path).verify(claim).verification_status,'supported')

    def test_missing_ocr_and_multipage(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'two.tiff'
            Image.new('RGB',(128,128),'white').save(path,save_all=True,append_images=[Image.new('RGB',(128,128),'white')])
            with patch('intelligence.engine.ocr',return_value=([],{'available':False,'confidence':0})), patch('intelligence.engine.run_forensics',return_value=([],{'ela':{'available':False}})):
                result=analyze(path,'two.tiff')
            self.assertEqual(result.document.pages,2)
            self.assertEqual(result.assessment.level,'MODERATE')
            self.assertEqual(result.assessment.confidence,round(.65*result.technical_details['coverage'],3))
            self.assertEqual(result.forensics,[])
            self.assertEqual([p['page'] for p in result.technical_details['pages']],[1,2])

    def test_blank_page_no_local_findings(self):
        from intelligence.forensics import local_signals
        self.assertEqual(local_signals(Image.new('RGB',(256,256),'white'),1),[])

    def test_split_groups_cross_labels(self):
        rows=[{'base_id':str(i),'label':label,'document_type':'invoice','filename':f'{i}-{label}'}
              for i in range(30) for label in ('genuine','forged')]
        partitions=create_grouped_splits(rows)
        result=audit([r for part in partitions for r in part])
        self.assertTrue(result['safe_to_train'])
        self.assertNotIn('split',rows[0])

    def test_metrics_known_values(self):
        result=metrics([{'label':1,'score':.9},{'label':1,'score':.2},{'label':0,'score':.8},{'label':0,'score':.1}])
        self.assertEqual(result['f1'],.5)
        self.assertEqual(result['false_positive_rate'],.5)
        self.assertEqual(result['roc_auc'],.75)
        self.assertIsNone(metrics([{'label':0,'score':.1}])['recall'])

    def test_api_upload_and_storage(self):
        from intelligence import api
        from starlette.datastructures import UploadFile
        with tempfile.TemporaryDirectory() as tmp:
            image=io.BytesIO();Image.new('RGB',(128,128),'white').save(image,format='PNG');image.seek(0)
            with patch.object(api,'STORE',Path(tmp)),patch('intelligence.engine.ocr',return_value=([],{'available':False,'confidence':0})):
                result=asyncio.run(api.upload(UploadFile(filename='sample.png',file=image)))
                self.assertEqual(api.get_analysis(result.document.id),result)
                self.assertEqual(api.get_report_data(result.document.id),result)
                self.assertEqual(api.get_technical(result.document.id),result.technical_details)
                with self.assertRaises(Exception): api.get_analysis('../outside')

    def test_api_rejects_mismatched_signature(self):
        from intelligence import api
        from starlette.datastructures import UploadFile
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(api.upload(UploadFile(filename='x.png',file=io.BytesIO(b'not an image'))))
        self.assertEqual(ctx.exception.status_code,400)

    def test_independent_detector_failure(self):
        from intelligence.forensics import run_forensics
        with patch('forgery_detector.perform_ela',side_effect=RuntimeError('fixture')):
            findings,diagnostics=run_forensics(Image.new('RGB',(128,128),'white'),1)
        self.assertFalse(diagnostics['ela']['available'])
        self.assertTrue(diagnostics['noise']['available'])

    def test_invalid_calendar_date(self):
        from intelligence.forensics import semantic_signals
        fields=extract(words('Date: 31/02/2026'),1)[1]
        self.assertEqual(len(semantic_signals(fields)),1)
        self.assertEqual(semantic_signals(extract(words('Date: 12/31/2026'),1)[1]),[])

    def test_synthetic_mask_covers_changed_pixels(self):
        from intelligence.synthetic import generate
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source.png'
            Image.new('RGB',(200,100),'gray').save(source)
            rows=generate(source,Path(tmp)/'generated',(10,10,60,30))
            for row in rows:
                if not row['localisation_applicable']: continue
                original=np.asarray(Image.open(row['original']).convert('RGB'))
                edited=np.asarray(Image.open(row['filename']).convert('RGB'))
                mask=np.asarray(Image.open(row['mask']))>0
                self.assertFalse(np.any(np.any(original!=edited,axis=2)&~mask))
            self.assertEqual(len({r['split'] for r in rows}),1)

    def test_localisation_metric(self):
        from intelligence.training import localisation_iou
        self.assertEqual(localisation_iou([[1,0]],[[1,1]]),.5)
        self.assertIsNone(localisation_iou([[0]],[[0]]))

    def test_openapi_contract(self):
        from main import app
        paths=app.openapi()['paths']
        self.assertIn('/api/analyze',paths)
        self.assertIn('/api/v1/analyze',paths)
        self.assertIn('/api/v1/analysis/{analysis_id}/report-data',paths)


if __name__=='__main__': unittest.main()
