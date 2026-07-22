
from sqlalchemy.orm import Session

from models.recipe import Recipe
from repositories.base import BaseRepository


class RecipeRepository(BaseRepository[Recipe]):
    def __init__(self, db: Session):
        super().__init__(Recipe, db)

    @property
    def model_type(self):
        return Recipe

    def get_by_household(self, household_id: str, skip: int = 0, limit: int = 100, q: str | None = None) -> list[Recipe]:
        query = self.db.query(Recipe).filter(Recipe.household_id == household_id)
        if q:
            query = query.filter(Recipe.title.ilike(f"%{q}%"))
        return query.offset(skip).limit(limit).all()

    def get_by_title(self, household_id: str, title: str) -> Recipe | None:
        return self.db.query(Recipe).filter(Recipe.household_id == household_id, Recipe.title == title).first()
