from fastapi import APIRouter, Depends

from es_app.progress.service import ProgressService, ProgressSummary

router = APIRouter(prefix="/progress", tags=["progress"])


def get_progress_service() -> ProgressService:
    raise NotImplementedError  # overridden in main


@router.get("/summary", response_model=ProgressSummary)
def get_summary(svc: ProgressService = Depends(get_progress_service)):
    return svc.get_summary()
