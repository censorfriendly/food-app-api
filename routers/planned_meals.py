from fastapi import APIRouter, HTTPException

from core.deps import CurrentUser, DbSession, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.planned_meal import PlannedMealCreate, PlannedMealUpdate
from services.planned_meal_service import PlannedMealService
from utils.logger import setup_logger

router = APIRouter(prefix="/api/v1/planned-meals", tags=["Planned Meals"])
logger = setup_logger()


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_planned_meal(
    payload: PlannedMealCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Add a recipe to a week plan."""
    try:
        household_id = get_household_id(current_user)
        service = PlannedMealService(db)
        data = service.add_recipe_to_week(
            household_id=household_id,
            recipe_id=payload.recipe_id,
            week_start=payload.week_start,
            day_of_week=payload.day_of_week,
            meal_time=payload.meal_time,
            notes=payload.notes,
        )
        return SuccessResponse(data=data)
    except AppError:
        raise
    except Exception as exc:
        logger.error(f"[create_planned_meal] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to create planned meal") from exc


@router.get("/{planned_meal_id}", response_model=SuccessResponse)
async def get_planned_meal(
    planned_meal_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    """Get a single planned meal by ID."""
    try:
        household_id = get_household_id(current_user)
        service = PlannedMealService(db)
        data = service.get_planned_meal(planned_meal_id, household_id)
        return SuccessResponse(data=data)
    except AppError:
        raise
    except Exception as exc:
        logger.error(f"[get_planned_meal] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to get planned meal") from exc


@router.put("/{planned_meal_id}", response_model=SuccessResponse)
async def update_planned_meal(
    planned_meal_id: str,
    payload: PlannedMealUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update a planned meal."""
    try:
        household_id = get_household_id(current_user)
        service = PlannedMealService(db)
        data = service.update_planned_meal(
            planned_meal_id, household_id, payload.model_dump(exclude_unset=True)
        )
        return SuccessResponse(data=data)
    except AppError:
        raise
    except Exception as exc:
        logger.error(f"[update_planned_meal] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to update planned meal") from exc


@router.delete("/{planned_meal_id}", response_model=SuccessResponse)
async def delete_planned_meal(
    planned_meal_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    """Soft-delete a planned meal."""
    try:
        household_id = get_household_id(current_user)
        service = PlannedMealService(db)
        success = service.delete_planned_meal(planned_meal_id, household_id)
        return SuccessResponse(data={"deleted": success})
    except AppError:
        raise
    except Exception as exc:
        logger.error(f"[delete_planned_meal] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to delete planned meal") from exc
