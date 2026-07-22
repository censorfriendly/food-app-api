import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.household import Household
from models.recipe import Recipe
from models.user import User
from schemas.recipe_ingredient import RecipeIngredientCreate

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_recipe_ing.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _create_authenticated_user(db) -> tuple[User, Household]:
    """Create a user with a household for testing."""
    # Create user first to satisfy household.owner_user_id FK constraint
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User",
    )
    db.add(user)
    db.flush()

    household = Household(name="Test Household", owner_user_id=user.id)
    db.add(household)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(household)
    return user, household


def _create_recipe(db, household_id: str) -> Recipe:
    """Create a recipe for testing."""
    recipe = Recipe(
        title="Test Recipe",
        household_id=household_id,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


class TestRecipeIngredientValidation:
    """Test validation of recipe ingredient creation payloads."""

    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        self.user, self.household = _create_authenticated_user(db_session)
        self.recipe = _create_recipe(db_session, self.household.id)

    def test_rejects_null_ingredient_id_with_null_ingredient_name(self):
        """When both ingredient_id and ingredient_name are null, validation should fail."""
        payload = {
            "ingredient_id": None,
            "ingredient_name": None,
            "quantity": 3,
            "measurement_unit_id": None,
            "optional": False,
            "display_order": 0,
        }

        with pytest.raises(ValidationError) as exc_info:
            RecipeIngredientCreate(**payload)

        assert "ingredient_id" in str(exc_info.value).lower() or "ingredient_name" in str(exc_info.value).lower()

    def test_accepts_null_ingredient_id_with_valid_ingredient_name(self):
        """When ingredient_name is provided, ingredient_id can be null."""
        payload = {
            "ingredient_id": None,
            "ingredient_name": "steak",
            "quantity": 3,
            "measurement_unit_id": None,
            "optional": False,
            "display_order": 0,
        }
        schema = RecipeIngredientCreate(**payload)
        assert schema.ingredient_name == "steak"
        assert schema.ingredient_id is None

    def test_rejects_negative_quantity(self):
        """Negative quantities should be rejected."""
        payload = {
            "ingredient_id": None,
            "ingredient_name": "steak",
            "quantity": -1,
            "measurement_unit_id": None,
            "optional": False,
            "display_order": 0,
        }

        with pytest.raises(ValidationError):
            RecipeIngredientCreate(**payload)

    def test_rejects_zero_quantity(self):
        """Zero quantity should be rejected."""
        payload = {
            "ingredient_id": None,
            "ingredient_name": "steak",
            "quantity": 0,
            "measurement_unit_id": None,
            "optional": False,
            "display_order": 0,
        }

        with pytest.raises(ValidationError):
            RecipeIngredientCreate(**payload)

    def test_accepts_positive_quantity(self):
        """Positive quantities should be accepted."""
        payload = {
            "ingredient_id": None,
            "ingredient_name": "steak",
            "quantity": 3,
            "measurement_unit_id": None,
            "optional": False,
            "display_order": 0,
        }
        schema = RecipeIngredientCreate(**payload)
        assert schema.quantity == 3

    def test_accepts_null_quantity(self):
        """Null quantity should be accepted."""
        payload = {
            "ingredient_id": None,
            "ingredient_name": "steak",
            "quantity": None,
            "measurement_unit_id": None,
            "optional": False,
            "display_order": 0,
        }
        schema = RecipeIngredientCreate(**payload)
        assert schema.quantity is None
