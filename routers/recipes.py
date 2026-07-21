from fastapi import APIRouter, HTTPException

from core.deps import DbSession, CurrentUser, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.recipe import RecipeCreate
from services.recipe_service import RecipeService

router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_recipe(payload: RecipeCreate, db: DbSession, current_user: CurrentUser):
    try:
        household_id = get_household_id(current_user)

        service = RecipeService(db)
        data = service.create_recipe(
            household_id=household_id,
            title=payload.title,
            description=payload.description,
            servings=payload.servings,
            prep_minutes=payload.prep_minutes,
            cook_minutes=payload.cook_minutes,
            notes=payload.notes,
            created_by=current_user["user"].id,
        )
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Recipe creation failed") from exc


@router.get("", response_model=SuccessResponse)
async def list_recipes(db: DbSession, current_user: CurrentUser, q: str | None = None):
    try:
        household_id = get_household_id(current_user)

        service = RecipeService(db)
        data = service.list_recipes(household_id, q=q)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Recipe listing failed") from exc
