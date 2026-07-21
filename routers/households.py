from fastapi import APIRouter, HTTPException

from core.deps import DbSession, CurrentUser
from exceptions.custom import AppError
from schemas.common import SuccessResponse
from schemas.household import DefaultHouseholdRequest, HouseholdCreate, HouseholdInviteRequest
from services.household_service import HouseholdService

router = APIRouter(prefix="/api/v1/households", tags=["Households"])


@router.get("", response_model=SuccessResponse)
async def list_households(db: DbSession, current_user: CurrentUser):
    household_service = HouseholdService(db)
    try:
        user = current_user["user"]
        data = household_service.list_user_households(user)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to load households") from exc


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_household(payload: HouseholdCreate, db: DbSession, current_user: CurrentUser):
    household_service = HouseholdService(db)
    try:
        user = current_user["user"]
        data = household_service.create_household(user, payload.name, payload.timezone)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Household creation failed") from exc


@router.patch("/default", response_model=SuccessResponse)
async def set_default_household(payload: DefaultHouseholdRequest, db: DbSession, current_user: CurrentUser):
    household_service = HouseholdService(db)
    try:
        user = current_user["user"]
        data = household_service.set_default_household(user, payload.household_id)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to update default household") from exc


@router.post("/{household_id}/invite", response_model=SuccessResponse)
async def invite_user_to_household(household_id: str, payload: HouseholdInviteRequest, db: DbSession, current_user: CurrentUser):
    household_service = HouseholdService(db)
    try:
        user = current_user["user"]
        data = household_service.invite_user_to_household(user, household_id, payload.email)
        return SuccessResponse(data=data)
    except AppError as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to invite household member") from exc
