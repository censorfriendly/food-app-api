from fastapi import APIRouter, HTTPException

from core.deps import CurrentUser, DbSession, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.recipe_ingredient import RecipeIngredientCreate, RecipeIngredientUpdate
from services.recipe_ingredient_service import RecipeIngredientService
from utils.logger import setup_logger

router = APIRouter(prefix="/api/v1/recipes/{recipe_id}/ingredients", tags=["Recipe Ingredients"])
logger = setup_logger()


@router.get("", response_model=SuccessResponse)
async def list_recipe_ingredients(recipe_id: str, db: DbSession, current_user: CurrentUser):
    """List all ingredients for a recipe."""
    try:
        household_id = get_household_id(current_user)
        service = RecipeIngredientService(db)
        service.verify_recipe(recipe_id, household_id)
        data = service.list_by_recipe(recipe_id)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[list_recipe_ingredients] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to list recipe ingredients") from exc


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_recipe_ingredient(
    recipe_id: str, payload: RecipeIngredientCreate, db: DbSession, current_user: CurrentUser
):
    """Add an ingredient to a recipe."""
    try:
        household_id = get_household_id(current_user)
        service = RecipeIngredientService(db)
        service.verify_recipe(recipe_id, household_id)
        resolved_ingredient = service.resolve_ingredient(
            household_id, payload.ingredient_id, payload.ingredient_name
        )
        data = service.create(
            recipe_id=recipe_id,
            ingredient=resolved_ingredient,
            quantity=payload.quantity,
            measurement_unit=payload.measurement_unit,
            optional=payload.optional,
            display_order=payload.display_order,
        )
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[create_recipe_ingredient] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to create recipe ingredient") from exc


@router.put("/{ingredient_id}", response_model=SuccessResponse)
async def update_recipe_ingredient(
    recipe_id: str,
    ingredient_id: str,
    payload: RecipeIngredientUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update a recipe ingredient."""
    try:
        household_id = get_household_id(current_user)
        service = RecipeIngredientService(db)
        service.verify_recipe(recipe_id, household_id)
        data = service.update(
            ingredient_id=ingredient_id,
            payload=payload.model_dump(exclude_unset=True),
        )
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[update_recipe_ingredient] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to update recipe ingredient") from exc


@router.delete("/{ingredient_id}", response_model=SuccessResponse)
async def delete_recipe_ingredient(
    recipe_id: str,
    ingredient_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    """Delete a recipe ingredient."""
    try:
        household_id = get_household_id(current_user)
        service = RecipeIngredientService(db)
        service.verify_recipe(recipe_id, household_id)
        success = service.delete(ingredient_id=ingredient_id)
        return SuccessResponse(data={"deleted": success})
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[delete_recipe_ingredient] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to delete recipe ingredient") from exc

