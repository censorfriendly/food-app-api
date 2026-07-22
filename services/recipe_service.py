from typing import Any

from sqlalchemy.orm import Session

from exceptions.custom import ConflictError, NotFoundError, ValidationError
from models.recipe import Recipe
from repositories.recipe_repository import RecipeRepository
from schemas.recipe import RecipeOut
from services.base import BaseService


class RecipeService(BaseService[Recipe]):
    def __init__(self, db: Session):
        super().__init__(db)
        self.recipe_repo = RecipeRepository(db)

    @property
    def repository(self):
        return self.recipe_repo

    def create_recipe(
        self,
        household_id: str,
        title: str,
        description: str | None = None,
        servings: int | None = None,
        prep_minutes: int | None = None,
        cook_minutes: int | None = None,
        notes: str | None = None,
        created_by: str | None = None,
    ) -> dict[str, Any]:
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

        return RecipeOut.model_validate(recipe).model_dump()

    def get_recipe(self, recipe_id: str, household_id: str) -> dict[str, Any]:
        recipe = self.recipe_repo.get_by_id(recipe_id)
        if not recipe or recipe.household_id != household_id:
            raise NotFoundError("Recipe not found")
        return RecipeOut.model_validate(recipe).model_dump()

    def update_recipe(
        self, recipe_id: str, household_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        recipe = self.recipe_repo.get_by_id(recipe_id)
        if not recipe or recipe.household_id != household_id:
            raise NotFoundError("Recipe not found")

        if payload.get("title"):
            existing = self.recipe_repo.get_by_title(household_id, payload["title"].strip())
            if existing and existing.id != recipe_id:
                raise ConflictError("Recipe already exists for this household")
            recipe.title = payload["title"].strip()

        for field in ("description", "servings", "prep_minutes", "cook_minutes", "notes"):
            if field in payload:
                setattr(recipe, field, payload[field])

        self.db.commit()
        self.db.refresh(recipe)
        return RecipeOut.model_validate(recipe).model_dump()

    def delete_recipe(self, recipe_id: str, household_id: str) -> bool:
        recipe = self.recipe_repo.get_by_id(recipe_id)
        if not recipe or recipe.household_id != household_id:
            raise NotFoundError("Recipe not found")

        recipe.is_deleted = True
        self.db.commit()
        return True

    def list_recipes(
        self, household_id: str, q: str | None = None
    ) -> list[dict[str, Any]]:
        recipes = self.recipe_repo.get_by_household(household_id, q=q)
        return [RecipeOut.model_validate(recipe).model_dump() for recipe in recipes]
