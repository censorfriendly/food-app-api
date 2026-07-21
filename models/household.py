from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.base import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from models.household_member import HouseholdMember
    from models.ingredient import Ingredient
    from models.recipe import Recipe
    from models.user import User
    from models.weekly_plan import WeeklyPlan
class Household(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "households"
    __table_args__ = (UniqueConstraint("name", "owner_user_id", name="uq_household_name_owner"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timezone: Mapped[str] = mapped_column(String(100), default="UTC", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    owner: Mapped["User"] = relationship(back_populates="households", foreign_keys=[owner_user_id])
    members: Mapped[list["HouseholdMember"]] = relationship(
        back_populates="household", cascade="all, delete-orphan"
    )
    ingredients: Mapped[list["Ingredient"]] = relationship(back_populates="household", cascade="all, delete-orphan")
    recipes: Mapped[list["Recipe"]] = relationship(back_populates="household", cascade="all, delete-orphan")
    weekly_plans: Mapped[list["WeeklyPlan"]] = relationship(
        back_populates="household", cascade="all, delete-orphan"
    )


