from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session, joinedload

from exceptions.custom import ConflictError, NotFoundError, ValidationError
from models.planned_meal import PlannedMeal
from models.weekly_plan import WeeklyPlan
from repositories.weekly_plan_repository import WeeklyPlanRepository
from schemas.weekly_plan import NestedPlannedMealOut, WeeklyPlanOut
from services.base import BaseService


class WeeklyPlanService(BaseService[WeeklyPlan]):
    def __init__(self, db: Session):
        super().__init__(db)
        self.weekly_plan_repo = WeeklyPlanRepository(db)

    @property
    def repository(self):
        return self.weekly_plan_repo

    @staticmethod
    def _serialize_plan(plan: WeeklyPlan) -> dict[str, Any]:
        """Serialize a weekly plan with nested planned meals and recipe details."""
        planned_meals_data = []
        for pm in plan.planned_meals:
            planned_meals_data.append(
                NestedPlannedMealOut(
                    id=pm.id,
                    recipe_id=pm.recipe_id,
                    day_of_week=pm.day_of_week,
                    meal_time=pm.meal_time,
                    notes=pm.notes,
                    recipe_title=pm.recipe.title if pm.recipe else None,
                    recipe_description=pm.recipe.description if pm.recipe else None,
                ).model_dump()
            )

        return WeeklyPlanOut(
            id=plan.id,
            household_id=plan.household_id,
            week_start=plan.week_start,
            created_by=plan.created_by,
            planned_meals=planned_meals_data,
        ).model_dump()

    def create_weekly_plan(self, household_id: str, week_start: date, created_by: str | None = None) -> dict[str, Any]:
        if week_start.weekday() != 0:
            raise ValidationError("week_start must be a Monday")

        existing = self.weekly_plan_repo.get_for_week(household_id, week_start)
        if existing:
            raise ConflictError("Weekly plan already exists for this household and week")

        weekly_plan = WeeklyPlan(household_id=household_id, week_start=week_start, created_by=created_by)
        self.db.add(weekly_plan)
        self.db.commit()
        self.db.refresh(weekly_plan)

        return self._serialize_plan(weekly_plan)

    def get(self, plan_id: str, household_id: str) -> dict[str, Any]:
        """Get a single weekly plan by ID with household verification."""
        plan = (
            self.db.query(WeeklyPlan)
            .options(joinedload(WeeklyPlan.planned_meals).joinedload(PlannedMeal.recipe))
            .filter(
                WeeklyPlan.id == plan_id,
                WeeklyPlan.household_id == household_id,
            )
            .first()
        )
        if not plan:
            raise NotFoundError("Weekly plan not found")
        return self._serialize_plan(plan)

    def list_weekly_plans(self, household_id: str) -> list[dict[str, Any]]:
        plans = self.weekly_plan_repo.get_by_household(household_id)
        # Eager load relationships for serialization
        for plan in plans:
            self.db.refresh(plan, ["planned_meals"])
            for pm in plan.planned_meals:
                self.db.refresh(pm, ["recipe"])
        return [self._serialize_plan(plan) for plan in plans]

    def list_weekly_plans_for_range(self, household_id: str, start_date: date, end_date: date) -> list[dict[str, Any]]:
        plans = self.weekly_plan_repo.get_by_household(household_id)
        filtered_plans = []
        for plan in plans:
            plan_start = plan.week_start
            plan_end = plan_start + timedelta(days=6)
            if plan_start <= end_date and plan_end >= start_date:
                filtered_plans.append(plan)

        # Eager load relationships for serialization
        for plan in filtered_plans:
            self.db.refresh(plan, ["planned_meals"])
            for pm in plan.planned_meals:
                self.db.refresh(pm, ["recipe"])
        return [self._serialize_plan(plan) for plan in filtered_plans]

    def update(self, plan_id: str, household_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Update a weekly plan."""
        plan = (
            self.db.query(WeeklyPlan)
            .filter(
                WeeklyPlan.id == plan_id,
                WeeklyPlan.household_id == household_id,
            )
            .first()
        )
        if not plan:
            raise NotFoundError("Weekly plan not found")

        for key, value in payload.items():
            if hasattr(plan, key) and value is not None:
                setattr(plan, key, value)
        self.db.commit()
        self.db.refresh(plan)
        self.db.refresh(plan, ["planned_meals"])
        for pm in plan.planned_meals:
            self.db.refresh(pm, ["recipe"])
        return self._serialize_plan(plan)

    def delete(self, plan_id: str, household_id: str) -> bool:
        """Soft-delete a weekly plan."""
        plan = (
            self.db.query(WeeklyPlan)
            .filter(
                WeeklyPlan.id == plan_id,
                WeeklyPlan.household_id == household_id,
            )
            .first()
        )
        if not plan:
            raise NotFoundError("Weekly plan not found")

        plan.is_deleted = True
        self.db.commit()
        return True
