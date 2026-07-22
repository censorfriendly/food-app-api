from datetime import date

from pydantic import BaseModel, Field


class ShoppingListRequest(BaseModel):
    week_start: date


class ShoppingListItemCreate(BaseModel):
    ingredient_id: str = Field(..., min_length=1, max_length=36)
    quantity: float | None = Field(default=None, gt=0)
    measurement_unit: str | None = Field(default=None, max_length=50)
    notes: str | None = None


class ShoppingListItemUpdate(BaseModel):
    checked: bool | None = None
    quantity: float | None = Field(default=None, gt=0)
    measurement_unit: str | None = Field(default=None, max_length=50)
    notes: str | None = None


class ShoppingListItemOut(BaseModel):
    id: str
    ingredient_id: str
    quantity: float | None = None
    measurement_unit: str | None = None
    checked: bool
    added_manually: bool
    notes: str | None = None

    model_config = {"from_attributes": True}


class ShoppingListOut(BaseModel):
    id: str
    weekly_plan_id: str
    week_start: date
    items: list[ShoppingListItemOut]

    model_config = {"from_attributes": True}

