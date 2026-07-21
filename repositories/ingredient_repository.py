from typing import Optional

from sqlalchemy.orm import Session

from models.ingredient import Ingredient
from repositories.base import BaseRepository


class IngredientRepository(BaseRepository[Ingredient]):
    def __init__(self, db: Session):
        super().__init__(Ingredient, db)

    @property
    def model_type(self):
        return Ingredient

    def get_by_household(self, household_id: str, skip: int = 0, limit: int = 100) -> list[Ingredient]:
        return (
            self.db.query(Ingredient)
            .filter(Ingredient.household_id == household_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_normalized_name(self, household_id: str, normalized_name: str) -> Optional[Ingredient]:
        return (
            self.db.query(Ingredient)
            .filter(Ingredient.household_id == household_id, Ingredient.normalized_name == normalized_name)
            .first()
        )

    def search(self, household_id: str, q: str, skip: int = 0, limit: int = 100) -> list[Ingredient]:
        """Search ingredients by name, case insensitive."""
        return (
            self.db.query(Ingredient)
            .filter(Ingredient.household_id == household_id)
            .filter(Ingredient.name.ilike(f"%{q}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )



