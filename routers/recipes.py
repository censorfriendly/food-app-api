from fastapi import APIRouter, HTTPException

from core.deps import CurrentUser, DbSession, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.recipe import RecipeCreate, RecipeUpdate
from services.recipe_service import RecipeService
from utils.logger import setup_logger

router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])
logger = setup_logger()


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_recipe(payload: RecipeCreate, db: DbSession, current_user: CurrentUser):
    """Create a new recipe for the household."""
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
        logger.error(f"[create_recipe] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to create recipe") from exc


@router.get("", response_model=SuccessResponse)
async def list_recipes(db: DbSession, current_user: CurrentUser, q: str | None = None):
    """List all recipes for the household."""
    try:
        household_id = get_household_id(current_user)

        service = RecipeService(db)
        data = service.list_recipes(household_id, q=q)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[list_recipes] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to list recipes") from exc


@router.get("/{recipe_id}", response_model=SuccessResponse)
async def get_recipe(recipe_id: str, db: DbSession, current_user: CurrentUser):
    """Get a single recipe by ID."""
    try:
        household_id = get_household_id(current_user)

        service = RecipeService(db)
        data = service.get_recipe(recipe_id, household_id)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[get_recipe] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to get recipe") from exc


@router.put("/{recipe_id}", response_model=SuccessResponse)
async def update_recipe(recipe_id: str, payload: RecipeUpdate, db: DbSession, current_user: CurrentUser):
    """Update a recipe."""
    try:
        household_id = get_household_id(current_user)

        service = RecipeService(db)
        data = service.update_recipe(recipe_id, household_id, payload.model_dump(exclude_unset=True))
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[update_recipe] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to update recipe") from exc


@router.delete("/{recipe_id}", response_model=SuccessResponse)
async def delete_recipe(recipe_id: str, db: DbSession, current_user: CurrentUser):
    """Soft-delete a recipe."""
    try:
        household_id = get_household_id(current_user)

        service = RecipeService(db)
        success = service.delete_recipe(recipe_id, household_id)
        return SuccessResponse(data={"deleted": success})
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[delete_recipe] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to delete recipe") from exc

