from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.base import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from models.shopping_list_item import ShoppingListItem
    from models.weekly_plan import WeeklyPlan


class ShoppingList(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "shopping_lists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    weekly_plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("weekly_plans.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )
    generated_at: Mapped[str | None] = mapped_column(String(64), nullable=True)

    weekly_plan: Mapped["WeeklyPlan"] = relationship(back_populates="shopping_list")
    items: Mapped[list["ShoppingListItem"]] = relationship(
        back_populates="shopping_list", cascade="all, delete-orphan"
    )
