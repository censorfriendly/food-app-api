from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from exceptions.custom import NotFoundError, ValidationError
from models.planned_meal import PlannedMeal
from models.recipe import Recipe
from models.weekly_plan import WeeklyPlan
from repositories.planned_meal_repository import PlannedMealRepository
from repositories.weekly_plan_repository import WeeklyPlanRepository
from schemas.planned_meal import PlannedMealOut
from services.base import BaseService

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
VALID_MEAL_TIMES = ["Breakfast", "Lunch", "Dinner", "Snack"]


class PlannedMealService(BaseService[PlannedMeal]):
    def __init__(self, db: Session):
        super().__init__(db)
        self.planned_meal_repo = PlannedMealRepository(db)
        self.weekly_plan_repo = WeeklyPlanRepository(db)

    @property
    def repository(self):
        return self.planned_meal_repo

    def _get_or_create_weekly_plan(self, household_id: str, week_start: date) -> WeeklyPlan:
        """Find or create the requested household week."""
        if week_start.weekday() != 0:
            raise ValidationError("week_start must be a Monday")

        plan = self.weekly_plan_repo.get_for_week(household_id, week_start)
        if plan:
            return plan

        plan = WeeklyPlan(household_id=household_id, week_start=week_start)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def _verify_recipe(self, recipe_id: str, household_id: str) -> Recipe:
        """Verify the recipe exists and belongs to the household."""
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

    def add_recipe_to_week(
        self,
        household_id: str,
        recipe_id: str,
        week_start: date,
        day_of_week: str,
        meal_time: str,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Orchestrate adding a recipe to the current week's plan.

        1. Verify the recipe belongs to the household.
        2. Find or create the requested week's plan.
        3. Create a planned recipe entry.
        """
        if day_of_week not in VALID_DAYS:
            raise ValidationError(f"Invalid day of week. Must be one of: {', '.join(VALID_DAYS)}")

        if meal_time not in VALID_MEAL_TIMES:
            raise ValidationError(f"Invalid meal time. Must be one of: {', '.join(VALID_MEAL_TIMES)}")

        self._verify_recipe(recipe_id, household_id)
        weekly_plan = self._get_or_create_weekly_plan(household_id, week_start)

        planned_meal = PlannedMeal(
            weekly_plan_id=weekly_plan.id,
            recipe_id=recipe_id,
            day_of_week=day_of_week,
            meal_time=meal_time,
            notes=notes,
        )
        self.db.add(planned_meal)
        self.db.commit()
        self.db.refresh(planned_meal)

        return PlannedMealOut.model_validate(planned_meal).model_dump()

    def get_planned_meal(self, planned_meal_id: str, household_id: str) -> dict[str, Any]:
        planned_meal = self.planned_meal_repo.get_by_id(planned_meal_id)
        if not planned_meal:
            raise NotFoundError("Planned meal not found")

        # Verify the weekly plan belongs to the household
        plan = self.weekly_plan_repo.get_by_id(planned_meal.weekly_plan_id)
        if not plan or plan.household_id != household_id:
            raise NotFoundError("Planned meal not found")

        return PlannedMealOut.model_validate(planned_meal).model_dump()

    def update_planned_meal(
        self,
        planned_meal_id: str,
        household_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        planned_meal = self.planned_meal_repo.get_by_id(planned_meal_id)
        if not planned_meal:
            raise NotFoundError("Planned meal not found")

        # Verify the weekly plan belongs to the household
        plan = self.weekly_plan_repo.get_by_id(planned_meal.weekly_plan_id)
        if not plan or plan.household_id != household_id:
            raise NotFoundError("Planned meal not found")

        if "recipe_id" in payload:
            self._verify_recipe(payload["recipe_id"], household_id)
            planned_meal.recipe_id = payload["recipe_id"]

        if "day_of_week" in payload:
            if payload["day_of_week"] not in VALID_DAYS:
                raise ValidationError(f"Invalid day of week. Must be one of: {', '.join(VALID_DAYS)}")
            planned_meal.day_of_week = payload["day_of_week"]

        if "meal_time" in payload:
            if payload["meal_time"] not in VALID_MEAL_TIMES:
                raise ValidationError(f"Invalid meal time. Must be one of: {', '.join(VALID_MEAL_TIMES)}")
            planned_meal.meal_time = payload["meal_time"]

        if "completed" in payload:
            planned_meal.completed = payload["completed"]

        if "notes" in payload:
            planned_meal.notes = payload["notes"]

        self.db.commit()
        self.db.refresh(planned_meal)
        return PlannedMealOut.model_validate(planned_meal).model_dump()

    def delete_planned_meal(self, planned_meal_id: str, household_id: str) -> bool:
        planned_meal = self.planned_meal_repo.get_by_id(planned_meal_id)
        if not planned_meal:
            raise NotFoundError("Planned meal not found")

        # Verify the weekly plan belongs to the household
        plan = self.weekly_plan_repo.get_by_id(planned_meal.weekly_plan_id)
        if not plan or plan.household_id != household_id:
            raise NotFoundError("Planned meal not found")

        planned_meal.is_deleted = True
        self.db.commit()
        return True
