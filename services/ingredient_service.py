from typing import Any

from sqlalchemy.orm import Session

from exceptions.custom import ConflictError, ValidationError
from models.ingredient import Ingredient
from repositories.ingredient_repository import IngredientRepository
from services.base import BaseService


class IngredientService(BaseService[Ingredient]):
    def __init__(self, db: Session):
        super().__init__(db)
        self.ingredient_repo = IngredientRepository(db)

    @property
    def repository(self):
        return self.ingredient_repo

    def create_ingredient(self, household_id: str, name: str, category: str | None = None) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValidationError("Ingredient name is required")

        normalized_name = name.strip().lower()
        existing = self.ingredient_repo.get_by_normalized_name(household_id, normalized_name)
        if existing:
            raise ConflictError("Ingredient already exists for this household")

        ingredient = Ingredient(
            household_id=household_id,
            name=name.strip(),
            normalized_name=normalized_name,
            category=category,
        )
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)

        return {
            "id": ingredient.id,
            "name": ingredient.name,
            "normalized_name": ingredient.normalized_name,
            "category": ingredient.category,
        }

    def list_ingredients(self, household_id: str) -> list[dict[str, Any]]:
        ingredients = self.ingredient_repo.get_by_household(household_id)
        return [
            {
                "id": ingredient.id,
                "name": ingredient.name,
                "normalized_name": ingredient.normalized_name,
                "category": ingredient.category,
            }
            for ingredient in ingredients
        ]

    def search_ingredients(self, household_id: str, q: str) -> list[dict[str, Any]]:
        """Search ingredients by name, case insensitive."""
        ingredients = self.ingredient_repo.search(household_id, q)
        return [
            {
                "id": ingredient.id,
                "name": ingredient.name,
                "normalized_name": ingredient.normalized_name,
                "category": ingredient.category,
            }
            for ingredient in ingredients
        ]

