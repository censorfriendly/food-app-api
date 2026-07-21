from fastapi import APIRouter, HTTPException, Query

from core.deps import DbSession, CurrentUser, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.ingredient import IngredientCreate
from services.ingredient_service import IngredientService

router = APIRouter(prefix="/api/v1/ingredients", tags=["Ingredients"])


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_ingredient(payload: IngredientCreate, db: DbSession, current_user: CurrentUser):
    try:
        household_id = get_household_id(current_user)

        service = IngredientService(db)
        data = service.create_ingredient(
            household_id=household_id,
            name=payload.name,
            category=payload.category,
        )
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Ingredient creation failed") from exc


@router.get("", response_model=SuccessResponse)
async def list_ingredients(db: DbSession, current_user: CurrentUser):
    try:
        household_id = get_household_id(current_user)

        service = IngredientService(db)
        data = service.list_ingredients(household_id)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Ingredient listing failed") from exc


@router.get("/search", response_model=SuccessResponse)
async def search_ingredients(db: DbSession, current_user: CurrentUser, q: str = Query(..., min_length=1)):
    try:
        household_id = get_household_id(current_user)

        service = IngredientService(db)
        data = service.search_ingredients(household_id, q)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Ingredient search failed") from exc


