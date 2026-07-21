from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.base import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from models.recipe import Recipe


class RecipeStep(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "recipe_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    recipe_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    instructions: Mapped[str] = mapped_column(String(4000), nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="steps")
