from datetime import date
from typing import Any

from sqlalchemy.orm import Session, joinedload

from exceptions.custom import NotFoundError, ValidationError
from models.ingredient import Ingredient
from models.shopping_list import ShoppingList
from models.shopping_list_item import ShoppingListItem
from models.weekly_plan import WeeklyPlan


class ShoppingListService:
    def __init__(self, db: Session):
        self.db = db

    def _get_plan(self, household_id: str, week_start: date) -> WeeklyPlan:
        if week_start.weekday() != 0:
            raise ValidationError("week_start must be a Monday")
        plan = (
            self.db.query(WeeklyPlan)
            .filter(
                WeeklyPlan.household_id == household_id,
                WeeklyPlan.week_start == week_start,
            )
            .first()
        )
        if not plan:
            raise NotFoundError("Weekly plan not found")
        return plan

    def _load_shopping_list(self, shopping_list_id: str) -> ShoppingList:
        """Load a shopping list with all relationships eager-loaded."""
        return (
            self.db.query(ShoppingList)
            .options(
                joinedload(ShoppingList.weekly_plan),
                joinedload(ShoppingList.items).joinedload(ShoppingListItem.ingredient),
            )
            .filter(ShoppingList.id == shopping_list_id)
            .first()
        )

    def _serialize(self, shopping_list: ShoppingList) -> dict[str, Any]:
        """Serialize shopping list with nested ingredient names."""
        return {
            "id": shopping_list.id,
            "weekly_plan_id": shopping_list.weekly_plan_id,
            "week_start": shopping_list.weekly_plan.week_start,
            "items": [
                {
                    "id": item.id,
                    "ingredient_id": item.ingredient_id,
                    "ingredient_name": item.ingredient.name,
                    "quantity": float(item.quantity) if item.quantity is not None else None,
                    "measurement_unit": item.measurement_unit,
                    "checked": item.checked,
                    "added_manually": item.added_manually,
                    "notes": item.notes,
                }
                for item in shopping_list.items
            ],
        }

    def get_for_week(self, household_id: str, week_start: date) -> dict[str, Any]:
        plan = self._get_plan(household_id, week_start)
        shopping_list = (
            self.db.query(ShoppingList)
            .options(
                joinedload(ShoppingList.weekly_plan),
                joinedload(ShoppingList.items).joinedload(ShoppingListItem.ingredient),
            )
            .filter(ShoppingList.weekly_plan_id == plan.id)
            .first()
        )
        if not shopping_list:
            raise NotFoundError("Shopping list not found")
        return self._serialize(shopping_list)

    def generate(self, household_id: str, week_start: date) -> dict[str, Any]:
        plan = self._get_plan(household_id, week_start)
        shopping_list = self.db.query(ShoppingList).filter(ShoppingList.weekly_plan_id == plan.id).first()
        if not shopping_list:
            shopping_list = ShoppingList(weekly_plan_id=plan.id)
            self.db.add(shopping_list)
            self.db.flush()
        else:
            shopping_list.items.clear()

        totals: dict[tuple[str, str | None], float | None] = {}
        for planned_meal in plan.planned_meals:
            for recipe_ingredient in planned_meal.recipe.ingredients:
                key = (recipe_ingredient.ingredient_id, recipe_ingredient.measurement_unit)
                if key not in totals:
                    totals[key] = None
                if recipe_ingredient.quantity is not None:
                    totals[key] = (totals[key] or 0) + float(recipe_ingredient.quantity)

        for (ingredient_id, measurement_unit), quantity in totals.items():
            shopping_list.items.append(
                ShoppingListItem(
                    ingredient_id=ingredient_id,
                    quantity=quantity,
                    measurement_unit=measurement_unit,
                    added_manually=False,
                )
            )
        self.db.commit()
        self.db.refresh(shopping_list)
        shopping_list = self._load_shopping_list(shopping_list.id)
        return self._serialize(shopping_list)

    def add_item(self, household_id: str, week_start: date, payload: dict[str, Any]) -> dict[str, Any]:
        plan = self._get_plan(household_id, week_start)
        shopping_list = self.db.query(ShoppingList).filter(ShoppingList.weekly_plan_id == plan.id).first()
        if not shopping_list:
            shopping_list = ShoppingList(weekly_plan_id=plan.id)
            self.db.add(shopping_list)
            self.db.flush()
        ingredient = (
            self.db.query(Ingredient)
            .filter(
                Ingredient.id == payload["ingredient_id"],
                Ingredient.household_id == household_id,
            )
            .first()
        )
        if not ingredient:
            raise NotFoundError("Ingredient not found")
        item = ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient_id=ingredient.id,
            quantity=payload.get("quantity"),
            measurement_unit=payload.get("measurement_unit"),
            notes=payload.get("notes"),
            added_manually=True,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(shopping_list)
        shopping_list = self._load_shopping_list(shopping_list.id)
        return self._serialize(shopping_list)

    def update_item(self, household_id: str, item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        item = (
            self.db.query(ShoppingListItem)
            .join(ShoppingList)
            .join(WeeklyPlan)
            .filter(
                ShoppingListItem.id == item_id,
                WeeklyPlan.household_id == household_id,
            )
            .first()
        )
        if not item:
            raise NotFoundError("Shopping list item not found")
        for field in ("checked", "quantity", "measurement_unit", "notes"):
            if field in payload and payload[field] is not None:
                setattr(item, field, payload[field])
        self.db.commit()
        shopping_list = self._load_shopping_list(item.shopping_list_id)
        return self._serialize(shopping_list)
