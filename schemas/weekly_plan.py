from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class WeeklyPlanCreate(BaseModel):
    week_start: date


class WeeklyPlanUpdate(BaseModel):
    week_start: Optional[date] = None


class NestedPlannedMealOut(BaseModel):
    """Planned meal flattened for weekly plan serialization."""
    id: str
    recipe_id: str
    day_of_week: str
    meal_time: str
    completed: bool = False
    notes: Optional[str] = None
    recipe_title: Optional[str] = None
    recipe_description: Optional[str] = None

    model_config = {"from_attributes": True}


class WeeklyPlanOut(BaseModel):
    id: str
    household_id: str
    week_start: date
    created_by: Optional[str] = None
    planned_meals: list[NestedPlannedMealOut] = []

    model_config = {"from_attributes": True}
