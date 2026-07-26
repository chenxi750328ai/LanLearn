from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from es_app.config import get_settings
from es_app.db import get_connection, init_db
from es_app.errors import register_exception_handlers
from es_app.exam.router import get_exam_service
from es_app.exam.router import router as exam_router
from es_app.exam.service import ExamService
from es_app.adapters.fake_ocr import FakeOcr
from es_app.adapters.tesseract_ocr import TesseractOcr, tesseract_available
from es_app.ingest.router import get_ingest_service
from es_app.ingest.router import router as ingest_router
from es_app.ingest.service import IngestService
from es_app.lexicon.router import get_lexicon_service
from es_app.lexicon.router import router as lexicon_router
from es_app.lexicon.seed import seed_builtin_toefl
from es_app.lexicon.service import LexiconService
from es_app.lexicon.store import LexiconStore
from es_app.plans.router import get_plan_service
from es_app.plans.router import router as plans_router
from es_app.plans.service import PlanService
from es_app.progress.router import get_progress_service
from es_app.progress.router import router as progress_router
from es_app.progress.service import ProgressService
from es_app.speech.router import router as speech_router
from es_app.study.router import get_study_service
from es_app.study.router import router as study_router
from es_app.study.service import StudyService

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"


def create_app() -> FastAPI:
    settings = get_settings()
    conn = get_connection(settings.data_dir)
    init_db(conn)

    lexicon_store = LexiconStore(conn)
    lexicon_service = LexiconService(lexicon_store)
    ocr = TesseractOcr() if tesseract_available() else FakeOcr(text="")
    ingest_service = IngestService(lexicon_service, ocr=ocr)
    seed_builtin_toefl(lexicon_service)
    plan_service = PlanService(conn, lexicon_store)
    study_service = StudyService(conn, lexicon_store, plan_service)
    exam_service = ExamService(conn, lexicon_store, plan_service)
    progress_service = ProgressService(conn)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.conn = conn
        yield
        conn.close()

    app = FastAPI(lifespan=lifespan)
    register_exception_handlers(app)

    app.dependency_overrides[get_plan_service] = lambda: plan_service
    app.dependency_overrides[get_lexicon_service] = lambda: lexicon_service
    app.dependency_overrides[get_ingest_service] = lambda: ingest_service
    app.dependency_overrides[get_study_service] = lambda: study_service
    app.dependency_overrides[get_exam_service] = lambda: exam_service
    app.dependency_overrides[get_progress_service] = lambda: progress_service

    app.include_router(plans_router)
    app.include_router(lexicon_router)
    app.include_router(ingest_router)
    app.include_router(study_router)
    app.include_router(exam_router)
    app.include_router(progress_router)
    app.include_router(speech_router)

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/ui", StaticFiles(directory=str(STATIC_DIR), html=True), name="ui")

    @app.get("/")
    def root():
        return RedirectResponse(url="/ui/", status_code=307)

    return app
