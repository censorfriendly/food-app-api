from fastapi import APIRouter, HTTPException

from core.deps import CurrentUser, DbSession, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.ingredient import IngredientCreate, IngredientUpdate
from services.ingredient_service import IngredientService
from utils.logger import setup_logger

router = APIRouter(prefix="/api/v1/ingredients", tags=["Ingredients"])
logger = setup_logger()


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_ingredient(payload: IngredientCreate, db: DbSession, current_user: CurrentUser):
    """Create a new ingredient for the household."""
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
        logger.error(f"[create_ingredient] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to create ingredient") from exc


@router.get("", response_model=SuccessResponse)
async def list_ingredients(db: DbSession, current_user: CurrentUser):
    """List all ingredients for the household."""
    try:
        household_id = get_household_id(current_user)

        service = IngredientService(db)
        data = service.list_ingredients(household_id)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[list_ingredients] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to list ingredients") from exc


@router.get("/{ingredient_id}", response_model=SuccessResponse)
async def get_ingredient(ingredient_id: str, db: DbSession, current_user: CurrentUser):
    """Get a single ingredient by ID."""
    try:
        household_id = get_household_id(current_user)

        service = IngredientService(db)
        data = service.get_ingredient(ingredient_id, household_id)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[get_ingredient] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to get ingredient") from exc


@router.put("/{ingredient_id}", response_model=SuccessResponse)
async def update_ingredient(ingredient_id: str, payload: IngredientUpdate, db: DbSession, current_user: CurrentUser):
    """Update an ingredient."""
    try:
        household_id = get_household_id(current_user)

        service = IngredientService(db)
        data = service.update_ingredient(ingredient_id, household_id, payload.model_dump(exclude_unset=True))
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[update_ingredient] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to update ingredient") from exc


@router.delete("/{ingredient_id}", response_model=SuccessResponse)
async def delete_ingredient(ingredient_id: str, db: DbSession, current_user: CurrentUser):
    """Soft-delete an ingredient."""
    try:
        household_id = get_household_id(current_user)

        service = IngredientService(db)
        success = service.delete_ingredient(ingredient_id, household_id)
        return SuccessResponse(data={"deleted": success})
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[delete_ingredient] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to delete ingredient") from exc


@router.get("/search", response_model=SuccessResponse)
async def search_ingredients(q: str, db: DbSession, current_user: CurrentUser):
    """Search ingredients by name, case insensitive."""
    try:
        household_id = get_household_id(current_user)

        service = IngredientService(db)
        data = service.search_ingredients(household_id, q)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        logger.error(f"[search_ingredients] Unexpected exception: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to search ingredients") from exc

