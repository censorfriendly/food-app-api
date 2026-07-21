from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.base import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from models.household import Household
    from models.recipe import Recipe


class Meal(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "meals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recipe_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    meal_type: Mapped[str] = mapped_column(String(50), default="Custom", nullable=False)

    household: Mapped["Household"] = relationship(back_populates="meals")
    recipe: Mapped["Recipe | None"] = relationship()
