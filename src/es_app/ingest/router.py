import asyncio

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from es_app.ingest.service import IngestService
from es_app.schemas.word import Word, WordCandidate

router = APIRouter(prefix="/ingest", tags=["ingest"])


def get_ingest_service() -> IngestService:
    raise NotImplementedError  # overridden in main


class FileIngestResponse(BaseModel):
    candidates: list[WordCandidate]
    failures: list[dict]


class ConfirmRequest(BaseModel):
    candidates: list[WordCandidate]


class ImageIngestResponse(BaseModel):
    candidates: list[WordCandidate]


@router.post("/file", response_model=FileIngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    svc: IngestService = Depends(get_ingest_service),
):
    content = (await file.read()).decode("utf-8")
    candidates, failures = svc.parse_file(file.filename or "upload.txt", content)
    return FileIngestResponse(candidates=candidates, failures=failures)


@router.post("/image", response_model=ImageIngestResponse)
async def ingest_image(
    file: UploadFile = File(...),
    svc: IngestService = Depends(get_ingest_service),
):
    image_bytes = await file.read()
    candidates = await asyncio.to_thread(svc.parse_image, image_bytes)
    return ImageIngestResponse(candidates=candidates)


@router.post("/confirm", response_model=list[Word])
def confirm_ingest(body: ConfirmRequest, svc: IngestService = Depends(get_ingest_service)):
    return svc.confirm(body.candidates)
