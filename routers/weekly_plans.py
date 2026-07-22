from datetime import date

from fastapi import APIRouter, HTTPException, Query

from core.deps import CurrentUser, DbSession, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.weekly_plan import WeeklyPlanCreate, WeeklyPlanUpdate
from services.weekly_plan_service import WeeklyPlanService

router = APIRouter(prefix="/api/v1/weekly-plans", tags=["Weekly Plans"])

# Module-level Query defaults to avoid B008 (function calls in argument defaults)
START_DATE_DEFAULT = Query(default=None)
END_DATE_DEFAULT = Query(default=None)


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
    start_date: date | None = START_DATE_DEFAULT,
    end_date: date | None = END_DATE_DEFAULT,
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


@router.get("/{plan_id}", response_model=SuccessResponse)
async def get_weekly_plan(plan_id: str, db: DbSession, current_user: CurrentUser):
    try:
        household_id = get_household_id(current_user)

        service = WeeklyPlanService(db)
        data = service.get(plan_id=plan_id, household_id=household_id)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to get weekly plan") from exc


@router.put("/{plan_id}", response_model=SuccessResponse)
async def update_weekly_plan(plan_id: str, payload: WeeklyPlanUpdate, db: DbSession, current_user: CurrentUser):
    try:
        household_id = get_household_id(current_user)

        service = WeeklyPlanService(db)
        data = service.update(
            plan_id=plan_id,
            household_id=household_id,
            payload=payload.model_dump(exclude_unset=True),
        )
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to update weekly plan") from exc


@router.delete("/{plan_id}", response_model=SuccessResponse)
async def delete_weekly_plan(plan_id: str, db: DbSession, current_user: CurrentUser):
    try:
        household_id = get_household_id(current_user)

        service = WeeklyPlanService(db)
        success = service.delete(plan_id=plan_id, household_id=household_id)
        return SuccessResponse(data={"deleted": success})
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to delete weekly plan") from exc
