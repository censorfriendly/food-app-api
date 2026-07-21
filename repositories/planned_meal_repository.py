from typing import Optional

from sqlalchemy.orm import Session

from models.planned_meal import PlannedMeal
from repositories.base import BaseRepository


class PlannedMealRepository(BaseRepository[PlannedMeal]):
    def __init__(self, db: Session):
        super().__init__(PlannedMeal, db)

    @property
    def model_type(self):
        return PlannedMeal

    def get_by_weekly_plan(
        self, weekly_plan_id: str, skip: int = 0, limit: int = 100
    ) -> list[PlannedMeal]:
        return (
            self.db.query(PlannedMeal)
            .filter(PlannedMeal.weekly_plan_id == weekly_plan_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
