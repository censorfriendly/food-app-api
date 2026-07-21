from datetime import date

from fastapi import APIRouter, HTTPException, Query

from core.deps import DbSession, CurrentUser, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.weekly_plan import WeeklyPlanCreate
from services.weekly_plan_service import WeeklyPlanService

router = APIRouter(prefix="/api/v1/weekly-plans", tags=["Weekly Plans"])


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_weekly_plan(payload: WeeklyPlanCreate, db: DbSession, current_user: CurrentUser):
    try:
        household_id = get_household_id(current_user)

        service = WeeklyPlanService(db)
        data = service.create_weekly_plan(
            household_id=household_id,
            week_start=payload.week_start,
            created_by=current_user["user"].id,
        )
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Weekly plan creation failed") from exc


@router.get("", response_model=SuccessResponse)
async def list_weekly_plans(
    db: DbSession,
    current_user: CurrentUser,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
):
    try:
        household_id = get_household_id(current_user)

        service = WeeklyPlanService(db)
        if start_date and end_date:
            data = service.list_weekly_plans_for_range(household_id, start_date, end_date)
        else:
            data = service.list_weekly_plans(household_id)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Weekly plan listing failed") from exc
