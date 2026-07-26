from fastapi import APIRouter, Depends
from pydantic import BaseModel

from es_app.exam.service import ExamReport, ExamService, ExamSession

router = APIRouter(prefix="/exam", tags=["exam"])


def get_exam_service() -> ExamService:
    raise NotImplementedError  # overridden in main


class CreateExamSessionRequest(BaseModel):
    plan_id: int
    question_count: int


class ExamAnswerItem(BaseModel):
    question_id: str
    choice: str


class SubmitExamRequest(BaseModel):
    answers: list[ExamAnswerItem]


@router.post("/sessions", response_model=ExamSession)
def create_session(
    body: CreateExamSessionRequest,
    svc: ExamService = Depends(get_exam_service),
):
    return svc.create_session(plan_id=body.plan_id, question_count=body.question_count)


@router.post("/sessions/{session_id}/submit", response_model=ExamReport)
def submit_session(
    session_id: str,
    body: SubmitExamRequest,
    svc: ExamService = Depends(get_exam_service),
):
    return svc.submit(
        session_id,
        answers=[a.model_dump() for a in body.answers],
    )
