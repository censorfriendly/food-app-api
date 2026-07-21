from typing import Any

from sqlalchemy.orm import Session, joinedload

from models.ingredient import Ingredient
from models.recipe_ingredient import RecipeIngredient
from schemas.recipe_ingredient import RecipeIngredientOut


class RecipeIngredientService:
    """Service for recipe ingredient operations with relationship-aware serialization."""

    def __init__(self, db: Session):
        self.db = db

    def list_by_recipe(self, recipe_id: str) -> list[dict[str, Any]]:
        """List all ingredients for a recipe, with ingredient details."""
        ingredients = (
            self.db.query(RecipeIngredient)
            .options(
                joinedload(RecipeIngredient.ingredient),
            )
            .filter(RecipeIngredient.recipe_id == recipe_id)
            .order_by(RecipeIngredient.display_order)
            .all()
        )
        return [RecipeIngredientOut.model_validate(ri).model_dump() for ri in ingredients]

    def create(
        self,
        recipe_id: str,
        ingredient: Ingredient,
        quantity: float | None,
        measurement_unit: str | None,
        optional: bool,
        display_order: int,
    ) -> dict[str, Any]:
        """Create a recipe ingredient and return serialized data."""
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe_id,
            ingredient_id=ingredient.id,
            quantity=quantity,
            measurement_unit=measurement_unit,
            optional=optional,
            display_order=display_order,
        )
        self.db.add(recipe_ingredient)
        self.db.commit()
        self.db.refresh(recipe_ingredient)

        # Eager-load relationships for serialization
        self.db.refresh(recipe_ingredient, ["ingredient"])
        return RecipeIngredientOut.model_validate(recipe_ingredient).model_dump()

