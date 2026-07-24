from fastapi import APIRouter

from es_app.errors import AppError

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/evaluate")
def evaluate():
    raise AppError(
        "ollama_unavailable",
        "发音评测尚未启用或 Ollama 不可用",
        status_code=503,
    )
