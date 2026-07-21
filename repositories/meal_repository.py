from typing import Optional

from sqlalchemy.orm import Session

from models.meal import Meal
from repositories.base import BaseRepository


class MealRepository(BaseRepository[Meal]):
    def __init__(self, db: Session):
        super().__init__(Meal, db)

    @property
    def model_type(self):
        return Meal

    def get_by_household(self, household_id: str, skip: int = 0, limit: int = 100) -> list[Meal]:
        return (
            self.db.query(Meal)
            .filter(Meal.household_id == household_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_title(self, household_id: str, title: str) -> Optional[Meal]:
        return self.db.query(Meal).filter(Meal.household_id == household_id, Meal.title == title).first()
