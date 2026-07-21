from typing import Optional

from pydantic import BaseModel, Field


class HouseholdCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    timezone: str = Field(default="UTC", max_length=100)


class HouseholdMemberOut(BaseModel):
    id: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class HouseholdListItem(BaseModel):
    id: str
    name: str
    timezone: str
    role: Optional[str] = None
    is_default: bool = False

    model_config = {"from_attributes": True}


class HouseholdOut(BaseModel):
    id: str
    name: str
    timezone: str
    owner: Optional[dict] = None

    model_config = {"from_attributes": True}


class DefaultHouseholdRequest(BaseModel):
    household_id: str = Field(..., min_length=1, max_length=36)


class HouseholdInviteRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
