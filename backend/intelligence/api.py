"""Versioned local API. Legacy upload routes remain unchanged."""
import json
import os
import re
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.concurrency import run_in_threadpool
from pypdfium2 import PdfiumError
from PIL import Image
from .schema import Analysis
from .engine import analyze

router = APIRouter(prefix='/api/v1', tags=['Proofly intelligence v1'])
STORE = Path(os.getenv('PROOFLY_REPORT_DIR', str(Path(__file__).resolve().parents[1] / 'analysis_results')))
LIMIT = 30 * 1024 * 1024
EXTENSIONS = {'.png','.jpg','.jpeg','.webp','.bmp','.tif','.tiff','.pdf'}


def read_report(analysis_id):
    if not re.fullmatch(r'[0-9a-f]{32}',analysis_id):
        raise HTTPException(404,'Analysis not found')
    try:
        return Analysis.model_validate_json((STORE / (analysis_id+'.json')).read_text(encoding='utf-8'))
    except FileNotFoundError:
        raise HTTPException(404,'Analysis not found')


def save_report(report):
    STORE.mkdir(parents=True,exist_ok=True)
    fd, name = tempfile.mkstemp(dir=STORE,suffix='.tmp')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as target:
            target.write(report.model_dump_json())
        os.replace(name, STORE / (report.document.id+'.json'))
    finally:
        if os.path.exists(name): os.unlink(name)


@router.post('/analyze',response_model=Analysis)
async def upload(file: UploadFile = File(...)):
    filename = (file.filename or 'upload').replace('\\','/').rsplit('/',1)[-1]
    ext = Path(filename).suffix.lower()
    if ext not in EXTENSIONS: raise HTTPException(400,'Unsupported format for v1; use an image or PDF')
    fd,path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(fd,'wb') as target:
            size = 0
            while chunk := await file.read(1024*1024):
                size += len(chunk)
                if size > LIMIT: raise HTTPException(413,'Upload exceeds 30 MB')
                target.write(chunk)
        if size == 0: raise HTTPException(400,'Empty upload')
        from main import validate_magic_bytes
        with open(path,'rb') as source:
            if not validate_magic_bytes(source.read(32),ext):
                raise HTTPException(400,'File signature does not match extension')
        try:
            report = await run_in_threadpool(analyze,path,filename)
        except (ValueError, OSError, PdfiumError, Image.DecompressionBombError) as exc:
            raise HTTPException(422,'Document could not be decoded or exceeded page/pixel limits') from exc
        await run_in_threadpool(save_report,report)
        return report
    finally:
        os.unlink(path)
        await file.close()


@router.get('/analysis/{analysis_id}',response_model=Analysis)
def get_analysis(analysis_id: str):
    return read_report(analysis_id)


@router.get('/analysis/{analysis_id}/technical')
def get_technical(analysis_id: str):
    return read_report(analysis_id).technical_details


@router.get('/analysis/{analysis_id}/report-data',response_model=Analysis)
def get_report_data(analysis_id: str):
    return read_report(analysis_id)


unversioned_router = APIRouter(prefix='/api', tags=['Proofly intelligence'])

@unversioned_router.get('/analysis/{analysis_id}', response_model=Analysis)
def get_analysis_unversioned(analysis_id: str):
    return read_report(analysis_id)


@unversioned_router.get('/analysis/{analysis_id}/technical')
def get_technical_unversioned(analysis_id: str):
    return read_report(analysis_id).technical_details


@unversioned_router.get('/analysis/{analysis_id}/report-data', response_model=Analysis)
def get_report_data_unversioned(analysis_id: str):
    return read_report(analysis_id)

