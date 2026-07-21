from typing import Optional

from pydantic import BaseModel, Field


class MealCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    meal_type: str = Field(default="Custom", max_length=50)
    notes: Optional[str] = None
    recipe_id: Optional[str] = None


class MealOut(BaseModel):
    id: str
    household_id: str
    title: str
    meal_type: str
    notes: Optional[str] = None
    recipe_id: Optional[str] = None

    model_config = {"from_attributes": True}
