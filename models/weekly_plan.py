from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.base import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from models.household import Household
    from models.planned_meal import PlannedMeal
    from models.shopping_list import ShoppingList


class WeeklyPlan(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "weekly_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    household: Mapped["Household"] = relationship(back_populates="weekly_plans")
    planned_meals: Mapped[list["PlannedMeal"]] = relationship(
        back_populates="weekly_plan", cascade="all, delete-orphan"
    )
    shopping_list: Mapped["ShoppingList | None"] = relationship(
        back_populates="weekly_plan", cascade="all, delete-orphan"
    )
