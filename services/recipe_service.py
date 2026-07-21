from typing import Any

from sqlalchemy.orm import Session

from exceptions.custom import ConflictError, ValidationError
from models.recipe import Recipe
from repositories.recipe_repository import RecipeRepository
from services.base import BaseService


class RecipeService(BaseService[Recipe]):
    def __init__(self, db: Session):
        super().__init__(db)
        self.recipe_repo = RecipeRepository(db)

    @property
    def repository(self):
        return self.recipe_repo

    def create_recipe(self, household_id: str, title: str, description: str | None = None, servings: int | None = None,
                      prep_minutes: int | None = None, cook_minutes: int | None = None, notes: str | None = None,
                      created_by: str | None = None) -> dict[str, Any]:
        if not title or not title.strip():
            raise ValidationError("Recipe title is required")

        existing = self.recipe_repo.get_by_title(household_id, title.strip())
        if existing:
            raise ConflictError("Recipe already exists for this household")

        recipe = Recipe(
            household_id=household_id,
            title=title.strip(),
            description=description,
            servings=servings,
            prep_minutes=prep_minutes,
            cook_minutes=cook_minutes,
            notes=notes,
            created_by=created_by,
        )
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)

        return {
            "id": recipe.id,
            "household_id": recipe.household_id,
            "title": recipe.title,
            "description": recipe.description,
            "servings": recipe.servings,
            "prep_minutes": recipe.prep_minutes,
            "cook_minutes": recipe.cook_minutes,
            "notes": recipe.notes,
        }

    def list_recipes(self, household_id: str, q: str | None = None) -> list[dict[str, Any]]:
        recipes = self.recipe_repo.get_by_household(household_id, q=q)
        return [
            {
                "id": recipe.id,
                "household_id": recipe.household_id,
                "title": recipe.title,
                "description": recipe.description,
                "servings": recipe.servings,
                "prep_minutes": recipe.prep_minutes,
                "cook_minutes": recipe.cook_minutes,
                "notes": recipe.notes,
            }
            for recipe in recipes
        ]
