from typing import Any

from sqlalchemy.orm import Session

from exceptions.custom import ConflictError, ValidationError
from models.meal import Meal
from repositories.meal_repository import MealRepository
from services.base import BaseService


class MealService(BaseService[Meal]):
    def __init__(self, db: Session):
        super().__init__(db)
        self.meal_repo = MealRepository(db)

    @property
    def repository(self):
        return self.meal_repo

    def create_meal(self, household_id: str, title: str, meal_type: str = "Custom", notes: str | None = None,
                    recipe_id: str | None = None) -> dict[str, Any]:
        if not title or not title.strip():
            raise ValidationError("Meal title is required")

        existing = self.meal_repo.get_by_title(household_id, title.strip())
        if existing:
            raise ConflictError("Meal already exists for this household")

        meal = Meal(
            household_id=household_id,
            title=title.strip(),
            meal_type=meal_type,
            notes=notes,
            recipe_id=recipe_id,
        )
        self.db.add(meal)
        self.db.commit()
        self.db.refresh(meal)

        return {
            "id": meal.id,
            "household_id": meal.household_id,
            "title": meal.title,
            "meal_type": meal.meal_type,
            "notes": meal.notes,
            "recipe_id": meal.recipe_id,
        }

    def list_meals(self, household_id: str) -> list[dict[str, Any]]:
        meals = self.meal_repo.get_by_household(household_id)
        return [
            {
                "id": meal.id,
                "household_id": meal.household_id,
                "title": meal.title,
                "meal_type": meal.meal_type,
                "notes": meal.notes,
                "recipe_id": meal.recipe_id,
            }
            for meal in meals
        ]
