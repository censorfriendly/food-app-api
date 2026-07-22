from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.base import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from models.household import Household
    from models.recipe_ingredient import RecipeIngredient


class Ingredient(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "ingredients"
    __table_args__ = (
        UniqueConstraint(
            "household_id",
            "normalized_name",
            name="uq_ingredients_household_normalized_name",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    household_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("households.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    household: Mapped[Household | None] = relationship(back_populates="ingredients")
    recipe_ingredients: Mapped[list[RecipeIngredient]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
