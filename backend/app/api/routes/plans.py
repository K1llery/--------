from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_plan_service
from app.schemas.plan import (
    PlanCreateRequest,
    PlanListResponse,
    PlanOut,
    PlanUpdateRequest,
)
from app.services.plan_service import PlanService

router = APIRouter()


@router.get("", response_model=PlanListResponse)
def list_plans(
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service),
) -> PlanListResponse:
    items = service.list_by_user(current_user["id"])
    return PlanListResponse(items=items)


@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(
    plan_id: int,
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service),
) -> PlanOut:
    plan = service.get_by_id(plan_id, current_user["id"])
    if plan is None:
        raise HTTPException(status_code=404, detail="计划不存在")
    return plan


@router.post("", response_model=PlanOut)
def create_plan(
    payload: PlanCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service),
) -> PlanOut:
    return service.create(current_user["id"], payload.model_dump())


@router.put("/{plan_id}", response_model=PlanOut)
def update_plan(
    plan_id: int,
    payload: PlanUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service),
) -> PlanOut:
    plan = service.update(plan_id, current_user["id"], payload.model_dump(exclude_unset=True))
    if plan is None:
        raise HTTPException(status_code=404, detail="计划不存在")
    return plan


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    current_user: dict = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service),
) -> dict:
    deleted = service.delete(plan_id, current_user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="计划不存在")
    return {"message": "删除成功"}
