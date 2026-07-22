
from pydantic import BaseModel, Field, model_validator


class IngredientOut(BaseModel):
    """Ingredient details returned as part of a recipe ingredient."""
    id: str
    name: str
    category: str | None = None

    model_config = {"from_attributes": True}


class RecipeIngredientCreate(BaseModel):
    ingredient_id: str | None = Field(default=None, max_length=36)
    ingredient_name: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: float | None = Field(default=None, gt=0)
    measurement_unit: str | None = Field(default=None, max_length=50)
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


class RecipeIngredientUpdate(BaseModel):
    quantity: float | None = Field(default=None, gt=0)
    measurement_unit: str | None = Field(default=None, max_length=50)
    optional: bool | None = None
    display_order: int | None = None


class RecipeIngredientOut(BaseModel):
    id: str
    recipe_id: str
    ingredient: IngredientOut
    quantity: float | None = None
    measurement_unit: str | None = None
    optional: bool = False
    display_order: int = 0

    model_config = {"from_attributes": True}


