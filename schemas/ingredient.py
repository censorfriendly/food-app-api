from typing import Optional

from pydantic import BaseModel, Field


class IngredientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)


class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)


class IngredientOut(BaseModel):
    id: str
    name: str
    normalized_name: str
    category: Optional[str] = None

    model_config = {"from_attributes": True}

