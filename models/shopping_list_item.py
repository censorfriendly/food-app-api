from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.base import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from models.ingredient import Ingredient
    from models.shopping_list import ShoppingList
class ShoppingListItem(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "shopping_list_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    shopping_list_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ingredient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    measurement_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    added_manually: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    shopping_list: Mapped[ShoppingList] = relationship(back_populates="items")
    ingredient: Mapped[Ingredient] = relationship()

