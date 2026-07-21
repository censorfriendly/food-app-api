from fastapi import APIRouter, HTTPException

from core.deps import DbSession, CurrentUser, get_household_id
from exceptions.custom import AppError
from models.ingredient import Ingredient
from models.recipe import Recipe
from schemas.common import SuccessResponse
from schemas.recipe_ingredient import RecipeIngredientCreate
from services.recipe_ingredient_service import RecipeIngredientService
from utils.logger import setup_logger

router = APIRouter(prefix="/api/v1/recipes/{recipe_id}/ingredients", tags=["Recipe Ingredients"])
logger = setup_logger()


def _resolve_ingredient(db: DbSession, household_id: str, ingredient_id: str | None, ingredient_name: str | None) -> Ingredient:
    """Resolve an ingredient by ID, by name, or create a new one."""
    if ingredient_id:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if ingredient:
            return ingredient
        raise HTTPException(status_code=404, detail="Ingredient not found")

    if ingredient_name:
        normalized_name = ingredient_name.strip().lower()
        ingredient = db.query(Ingredient).filter(
            Ingredient.normalized_name == normalized_name,
            Ingredient.household_id == household_id
        ).first()
        if ingredient:
            return ingredient

        ingredient = Ingredient(
            household_id=household_id,
            name=ingredient_name.strip(),
            normalized_name=normalized_name,
        )
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
        return ingredient

    raise HTTPException(status_code=400, detail="Either ingredient_id or ingredient_name must be provided")


def _verify_recipe(db: DbSession, recipe_id: str, household_id: str) -> Recipe:
    """Verify the recipe exists and belongs to the user's household."""
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id, Recipe.household_id == household_id
    ).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.get("", response_model=SuccessResponse)
async def list_recipe_ingredients(recipe_id: str, db: DbSession, current_user: CurrentUser):
    """List all ingredients for a recipe."""
    try:
        household_id = get_household_id(current_user)
        _verify_recipe(db, recipe_id, household_id)

        service = RecipeIngredientService(db)
        data = service.list_by_recipe(recipe_id)
        return SuccessResponse(data=data)
    except HTTPException:
        raise
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[list_recipe_ingredients] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to list recipe ingredients") from exc


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_recipe_ingredient(recipe_id: str, payload: RecipeIngredientCreate, db: DbSession, current_user: CurrentUser):
    """Add an ingredient to a recipe."""
    try:
        household_id = get_household_id(current_user)
        _verify_recipe(db, recipe_id, household_id)
        resolved_ingredient = _resolve_ingredient(
        db, household_id, payload.ingredient_id, payload.ingredient_name
        )

        service = RecipeIngredientService(db)
        data = service.create(
            recipe_id=recipe_id,
            ingredient=resolved_ingredient,
            quantity=payload.quantity,
            measurement_unit=payload.measurement_unit,
            optional=payload.optional,
            display_order=payload.display_order,
        )
        return SuccessResponse(data=data)
    except HTTPException:
        raise
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[create_recipe_ingredient] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to create recipe ingredient") from exc


