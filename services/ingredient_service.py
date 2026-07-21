from typing import Any

from sqlalchemy.orm import Session

from exceptions.custom import ConflictError, NotFoundError, ValidationError
from models.ingredient import Ingredient
from repositories.ingredient_repository import IngredientRepository
from schemas.ingredient import IngredientOut
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

        return IngredientOut.model_validate(ingredient).model_dump()

    def get_ingredient(self, ingredient_id: str, household_id: str) -> dict[str, Any]:
        ingredient = self.ingredient_repo.get_by_id(ingredient_id)
        if not ingredient or ingredient.household_id != household_id:
            raise NotFoundError("Ingredient not found")
        return IngredientOut.model_validate(ingredient).model_dump()

    def update_ingredient(self, ingredient_id: str, household_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        ingredient = self.ingredient_repo.get_by_id(ingredient_id)
        if not ingredient or ingredient.household_id != household_id:
            raise NotFoundError("Ingredient not found")

        if "name" in payload and payload["name"]:
            normalized_name = payload["name"].strip().lower()
            existing = self.ingredient_repo.get_by_normalized_name(household_id, normalized_name)
            if existing and existing.id != ingredient_id:
                raise ConflictError("Ingredient already exists for this household")
            ingredient.name = payload["name"].strip()
            ingredient.normalized_name = normalized_name

        if "category" in payload:
            ingredient.category = payload["category"]

        self.db.commit()
        self.db.refresh(ingredient)
        return IngredientOut.model_validate(ingredient).model_dump()

    def delete_ingredient(self, ingredient_id: str, household_id: str) -> bool:
        ingredient = self.ingredient_repo.get_by_id(ingredient_id)
        if not ingredient or ingredient.household_id != household_id:
            raise NotFoundError("Ingredient not found")

        ingredient.is_deleted = True
        self.db.commit()
        return True
    def list_ingredients(self, household_id: str) -> list[dict[str, Any]]:
        ingredients = self.ingredient_repo.get_by_household(household_id)
        return [IngredientOut.model_validate(ingredient).model_dump() for ingredient in ingredients]
    def search_ingredients(self, household_id: str, q: str) -> list[dict[str, Any]]:
        """Search ingredients by name, case insensitive."""
        ingredients = self.ingredient_repo.search(household_id, q)
        return [IngredientOut.model_validate(ingredient).model_dump() for ingredient in ingredients]

