from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from exceptions.custom import ConflictError, ValidationError
from models.planned_meal import PlannedMeal
from models.weekly_plan import WeeklyPlan
from repositories.weekly_plan_repository import WeeklyPlanRepository
from services.base import BaseService


class WeeklyPlanService(BaseService[WeeklyPlan]):
    def __init__(self, db: Session):
        super().__init__(db)
        self.weekly_plan_repo = WeeklyPlanRepository(db)

    @property
    def repository(self):
        return self.weekly_plan_repo

    def create_weekly_plan(self, household_id: str, week_start: str, created_by: str | None = None) -> dict[str, Any]:
        if not week_start:
            raise ValidationError("week_start is required")

        existing = self.weekly_plan_repo.get_for_week(household_id, week_start)
        if existing:
            raise ConflictError("Weekly plan already exists for this household and week")

        weekly_plan = WeeklyPlan(household_id=household_id, week_start=week_start, created_by=created_by)
        self.db.add(weekly_plan)
        self.db.commit()
        self.db.refresh(weekly_plan)

        return {
            "id": weekly_plan.id,
            "household_id": weekly_plan.household_id,
            "week_start": weekly_plan.week_start,
            "created_by": weekly_plan.created_by,
        }

    def list_weekly_plans(self, household_id: str) -> list[dict[str, Any]]:
        plans = self.weekly_plan_repo.get_by_household(household_id)
        return [
            {
                "id": plan.id,
                "household_id": plan.household_id,
                "week_start": plan.week_start,
                "created_by": plan.created_by,
                "planned_meals": [
                    {
                        "id": planned_meal.id,
                        "meal_id": planned_meal.meal_id,
                        "day_of_week": planned_meal.day_of_week,
                        "meal_time": planned_meal.meal_time,
                        "notes": planned_meal.notes,
                        "meal": {
                            "id": planned_meal.meal.id,
                            "title": planned_meal.meal.title,
                            "meal_type": planned_meal.meal.meal_type,
                            "notes": planned_meal.meal.notes,
                        },
                    }
                    for planned_meal in plan.planned_meals
                ],
            }
            for plan in plans
        ]

    def list_weekly_plans_for_range(self, household_id: str, start_date: date, end_date: date) -> list[dict[str, Any]]:
        plans = self.weekly_plan_repo.get_by_household(household_id)
        filtered_plans = []
        for plan in plans:
            plan_start = plan.week_start
            plan_end = plan_start + timedelta(days=6)
            if plan_start <= end_date and plan_end >= start_date:
                filtered_plans.append(plan)

        return [
            {
                "id": plan.id,
                "household_id": plan.household_id,
                "week_start": plan.week_start,
                "created_by": plan.created_by,
                "planned_meals": [
                    {
                        "id": planned_meal.id,
                        "meal_id": planned_meal.meal_id,
                        "day_of_week": planned_meal.day_of_week,
                        "meal_time": planned_meal.meal_time,
                        "notes": planned_meal.notes,
                        "meal": {
                            "id": planned_meal.meal.id,
                            "title": planned_meal.meal.title,
                            "meal_type": planned_meal.meal.meal_type,
                            "notes": planned_meal.meal.notes,
                        },
                    }
                    for planned_meal in plan.planned_meals
                ],
            }
            for plan in filtered_plans
        ]
