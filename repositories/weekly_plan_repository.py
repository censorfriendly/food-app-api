from typing import Optional

from sqlalchemy.orm import Session

from models.weekly_plan import WeeklyPlan
from repositories.base import BaseRepository


class WeeklyPlanRepository(BaseRepository[WeeklyPlan]):
    def __init__(self, db: Session):
        super().__init__(WeeklyPlan, db)

    @property
    def model_type(self):
        return WeeklyPlan

    def get_by_household(self, household_id: str, skip: int = 0, limit: int = 100) -> list[WeeklyPlan]:
        return (
            self.db.query(WeeklyPlan)
            .filter(WeeklyPlan.household_id == household_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_for_week(self, household_id: str, week_start: str) -> Optional[WeeklyPlan]:
        return (
            self.db.query(WeeklyPlan)
            .filter(WeeklyPlan.household_id == household_id, WeeklyPlan.week_start == week_start)
            .first()
        )
