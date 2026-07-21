from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.base import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from models.recipe import Recipe
    from models.weekly_plan import WeeklyPlan


class PlannedMeal(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "planned_meals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    weekly_plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("weekly_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recipe_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)
    meal_time: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    weekly_plan: Mapped["WeeklyPlan"] = relationship(back_populates="planned_meals")
    recipe: Mapped["Recipe"] = relationship()
