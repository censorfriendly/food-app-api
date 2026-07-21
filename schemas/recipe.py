from typing import Optional

from pydantic import BaseModel, Field


class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    servings: Optional[int] = None
    prep_minutes: Optional[int] = None
    cook_minutes: Optional[int] = None
    notes: Optional[str] = None


class RecipeOut(BaseModel):
    id: str
    household_id: str
    title: str
    description: Optional[str] = None
    servings: Optional[int] = None
    prep_minutes: Optional[int] = None
    cook_minutes: Optional[int] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
