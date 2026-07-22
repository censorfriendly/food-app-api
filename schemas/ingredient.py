
from pydantic import BaseModel, Field


class IngredientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str | None = Field(None, max_length=100)


class IngredientUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, max_length=100)


class IngredientOut(BaseModel):
    id: str
    name: str
    normalized_name: str
    category: str | None = None

    model_config = {"from_attributes": True}

