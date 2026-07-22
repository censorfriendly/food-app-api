from datetime import date

from pydantic import BaseModel


class WeeklyPlanCreate(BaseModel):
    week_start: date


class WeeklyPlanUpdate(BaseModel):
    week_start: date | None = None


class NestedPlannedMealOut(BaseModel):
    """Planned meal flattened for weekly plan serialization."""
    id: str
    recipe_id: str
    day_of_week: str
    meal_time: str
    completed: bool = False
    notes: str | None = None
    recipe_title: str | None = None
    recipe_description: str | None = None

    model_config = {"from_attributes": True}


class WeeklyPlanOut(BaseModel):
    id: str
    household_id: str
    week_start: date
    created_by: str | None = None
    planned_meals: list[NestedPlannedMealOut] = []

    model_config = {"from_attributes": True}
