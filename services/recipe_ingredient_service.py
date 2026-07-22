from typing import Any

from sqlalchemy.orm import Session, joinedload

from exceptions.custom import NotFoundError, ValidationError
from models.ingredient import Ingredient
from models.recipe import Recipe
from models.recipe_ingredient import RecipeIngredient
from schemas.recipe_ingredient import RecipeIngredientOut


class RecipeIngredientService:
    """Service for recipe ingredient operations with relationship-aware serialization."""

    def __init__(self, db: Session):
        self.db = db

    def verify_recipe(self, recipe_id: str, household_id: str) -> Recipe:
        """Verify the recipe exists and belongs to the user's household."""
        recipe = (
            self.db.query(Recipe)
            .filter(
                Recipe.id == recipe_id,
                Recipe.household_id == household_id,
            )
            .first()
        )
        if not recipe:
            raise NotFoundError("Recipe not found")
        return recipe

    def resolve_ingredient(
        self, household_id: str, ingredient_id: str | None, ingredient_name: str | None
    ) -> Ingredient:
        """Resolve an ingredient by ID, by name, or create a new one."""
        if ingredient_id:
            ingredient = (
                self.db.query(Ingredient)
                .filter(
                    Ingredient.id == ingredient_id,
                    Ingredient.household_id == household_id,
                )
                .first()
            )
            if ingredient:
                return ingredient
            raise NotFoundError("Ingredient not found")

        if ingredient_name:
            normalized_name = ingredient_name.strip().lower()
            ingredient = (
                self.db.query(Ingredient)
                .filter(
                    Ingredient.normalized_name == normalized_name,
                    Ingredient.household_id == household_id,
                )
                .first()
            )
            if ingredient:
                return ingredient

            ingredient = Ingredient(
                household_id=household_id,
                name=ingredient_name.strip(),
                normalized_name=normalized_name,
            )
            self.db.add(ingredient)
            self.db.commit()
            self.db.refresh(ingredient)
            return ingredient

        raise ValidationError("Either ingredient_id or ingredient_name must be provided")

    def list_by_recipe(self, recipe_id: str) -> list[dict[str, Any]]:
        """List all ingredients for a recipe, with ingredient details."""
        ingredients = (
            self.db.query(RecipeIngredient)
            .options(joinedload(RecipeIngredient.ingredient))
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

    def update(self, ingredient_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Update a recipe ingredient and return serialized data."""
        recipe_ingredient = (
            self.db.query(RecipeIngredient)
            .filter(
                RecipeIngredient.id == ingredient_id,
            )
            .first()
        )
        if not recipe_ingredient:
            raise NotFoundError("Recipe ingredient not found")

        for key, value in payload.items():
            if hasattr(recipe_ingredient, key) and value is not None:
                setattr(recipe_ingredient, key, value)

        self.db.commit()
        self.db.refresh(recipe_ingredient)

        # Eager-load relationships for serialization
        self.db.refresh(recipe_ingredient, ["ingredient"])
        return RecipeIngredientOut.model_validate(recipe_ingredient).model_dump()

    def delete(self, ingredient_id: str) -> bool:
        """Soft-delete a recipe ingredient."""
        recipe_ingredient = (
            self.db.query(RecipeIngredient)
            .filter(
                RecipeIngredient.id == ingredient_id,
            )
            .first()
        )
        if not recipe_ingredient:
            raise NotFoundError("Recipe ingredient not found")

        recipe_ingredient.is_deleted = True
        self.db.commit()
        return True
