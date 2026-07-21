from fastapi import APIRouter, HTTPException

from core.deps import DbSession, CurrentUser, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.meal import MealCreate
from services.meal_service import MealService

router = APIRouter(prefix="/api/v1/meals", tags=["Meals"])


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_meal(payload: MealCreate, db: DbSession, current_user: CurrentUser):
    try:
        household_id = get_household_id(current_user)

        service = MealService(db)
        data = service.create_meal(
            household_id=household_id,
            title=payload.title,
            meal_type=payload.meal_type,
            notes=payload.notes,
            recipe_id=payload.recipe_id,
        )
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Meal creation failed") from exc


@router.get("", response_model=SuccessResponse)
async def list_meals(db: DbSession, current_user: CurrentUser):
    try:
        household_id = get_household_id(current_user)

        service = MealService(db)
        data = service.list_meals(household_id)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Meal listing failed") from exc
