from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class IngredientOut(BaseModel):
    """Ingredient details returned as part of a recipe ingredient."""
    id: str
    name: str
    category: Optional[str] = None

    model_config = {"from_attributes": True}


class RecipeIngredientCreate(BaseModel):
    ingredient_id: Optional[str] = Field(default=None, max_length=36)
    ingredient_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    quantity: Optional[float] = Field(default=None, gt=0)
    measurement_unit: Optional[str] = Field(default=None, max_length=50)
    optional: bool = False
    display_order: int = 0

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def check_ingredient_source(self):
        if not self.ingredient_id and not self.ingredient_name:
            raise ValueError(
                "Either ingredient_id or ingredient_name must be provided"
            )
        return self


class RecipeIngredientOut(BaseModel):
    id: str
    recipe_id: str
    ingredient: IngredientOut
    quantity: Optional[float] = None
    measurement_unit: Optional[str] = None
    optional: bool = False
    display_order: int = 0

    model_config = {"from_attributes": True}


