from fastapi import APIRouter, Depends
from pydantic import BaseModel

from es_app.study.service import AnswerResult, StudyService, StudySession

router = APIRouter(prefix="/study", tags=["study"])


def get_study_service() -> StudyService:
    raise NotImplementedError  # overridden in main


class CreateStudySessionRequest(BaseModel):
    plan_id: int
    day_index: int
    mode: str


class StudyAnswerRequest(BaseModel):
    word_id: int
    answer: str


@router.post("/sessions", response_model=StudySession)
def create_session(
    body: CreateStudySessionRequest,
    svc: StudyService = Depends(get_study_service),
):
    return svc.create_session(
        plan_id=body.plan_id,
        day_index=body.day_index,
        mode=body.mode,  # type: ignore[arg-type]
    )


@router.post("/sessions/{session_id}/answer", response_model=AnswerResult)
def answer_session(
    session_id: str,
    body: StudyAnswerRequest,
    svc: StudyService = Depends(get_study_service),
):
    return svc.answer(session_id, word_id=body.word_id, answer=body.answer)
