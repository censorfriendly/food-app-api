from fastapi import APIRouter, HTTPException

from core.deps import CurrentUser, DbSession, get_household_id
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.shopping_list import (
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingListRequest,
)
from services.shopping_list_service import ShoppingListService

router = APIRouter(prefix="/api/v1/shopping-lists", tags=["Shopping Lists"])


def _service_error(exc: Exception, message: str) -> None:
    if isinstance(exc, AppError):
        raise exc
    raise HTTPException(status_code=500, detail=message) from exc


@router.get("", response_model=SuccessResponse)
async def get_shopping_list(
    week_start: str,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        from datetime import date

        household_id = get_household_id(current_user)
        data = ShoppingListService(db).get_for_week(household_id, date.fromisoformat(week_start))
        return SuccessResponse(data=data)
    except AppError:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="week_start must be YYYY-MM-DD") from exc
    except Exception as exc:
        _service_error(exc, "Unable to load shopping list")


@router.post("/generate", response_model=SuccessResponse)
async def generate_shopping_list(
    payload: ShoppingListRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        household_id = get_household_id(current_user)
        data = ShoppingListService(db).generate(household_id, payload.week_start)
        return SuccessResponse(data=data)
    except AppError:
        raise
    except Exception as exc:
        _service_error(exc, "Unable to generate shopping list")


@router.post("/items", response_model=SuccessResponse, status_code=201)
async def add_shopping_list_item(
    payload: ShoppingListItemCreate,
    week_start: str,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        from datetime import date

        household_id = get_household_id(current_user)
        data = ShoppingListService(db).add_item(
            household_id,
            date.fromisoformat(week_start),
            payload.model_dump(),
        )
        return SuccessResponse(data=data)
    except AppError:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="week_start must be YYYY-MM-DD") from exc
    except Exception as exc:
        _service_error(exc, "Unable to add shopping list item")


@router.patch("/items/{item_id}", response_model=SuccessResponse)
async def update_shopping_list_item(
    item_id: str,
    payload: ShoppingListItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        household_id = get_household_id(current_user)
        data = ShoppingListService(db).update_item(
            household_id,
            item_id,
            payload.model_dump(exclude_unset=True),
        )
        return SuccessResponse(data=data)
    except AppError:
        raise
    except Exception as exc:
        _service_error(exc, "Unable to update shopping list item")
