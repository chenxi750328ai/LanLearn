from fastapi import APIRouter, Depends
from pydantic import BaseModel

from es_app.plans.service import Plan, PlanService

router = APIRouter(prefix="/plans", tags=["plans"])


def get_plan_service() -> PlanService:
    raise NotImplementedError  # overridden in main


class CreatePlanRequest(BaseModel):
    exam_type: str
    daily_quota: int


@router.post("", response_model=Plan)
def create_plan(body: CreatePlanRequest, svc: PlanService = Depends(get_plan_service)):
    return svc.create_plan(exam_type=body.exam_type, daily_quota=body.daily_quota)


@router.get("/{plan_id}", response_model=Plan)
def get_plan(plan_id: int, svc: PlanService = Depends(get_plan_service)):
    return svc.get_plan(plan_id)
