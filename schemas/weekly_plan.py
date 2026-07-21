from typing import Optional

from pydantic import BaseModel, Field


class WeeklyPlanCreate(BaseModel):
    week_start: str = Field(..., min_length=1, max_length=20)


class WeeklyPlanOut(BaseModel):
    id: str
    household_id: str
    week_start: str
    created_by: Optional[str] = None

    model_config = {"from_attributes": True}
