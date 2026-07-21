from datetime import date

from pydantic import BaseModel, Field


class PlannedMealCreate(BaseModel):
    recipe_id: str = Field(..., min_length=1, max_length=36)
    week_start: date
    day_of_week: str = Field(..., min_length=1, max_length=20)
    meal_time: str = Field(..., min_length=1, max_length=20)
    notes: str | None = None


class PlannedMealUpdate(BaseModel):
    recipe_id: str | None = Field(None, min_length=1, max_length=36)
    day_of_week: str | None = Field(None, min_length=1, max_length=20)
    meal_time: str | None = Field(None, min_length=1, max_length=20)
    notes: str | None = None


class PlannedMealOut(BaseModel):
    id: str
    weekly_plan_id: str
    recipe_id: str
    day_of_week: str
    meal_time: str
    notes: str | None = None

    model_config = {"from_attributes": True}
