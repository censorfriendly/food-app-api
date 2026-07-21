"""replace_measurement_units_table_with_string_column

Drop the measurement_units table and replace measurement_unit_id foreign key
columns with simple measurement_unit string columns on recipe_ingredients
and shopping_list_items. Existing data is migrated by joining to the
measurement_units table to copy unit names.

Revision ID: bddbfc15a86c
Revises:
Create Date: 2026-07-21 16:08:22.123253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bddbfc15a86c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add new measurement_unit string columns
    op.add_column(
        "recipe_ingredients",
        sa.Column("measurement_unit", sa.String(50), nullable=True),
    )
    op.add_column(
        "shopping_list_items",
        sa.Column("measurement_unit", sa.String(50), nullable=True),
    )

    # Step 2: Copy unit names from measurement_units table into the new columns
    op.execute(
        """
        UPDATE recipe_ingredients
        SET measurement_unit = mu.name
        FROM measurement_units mu
        WHERE recipe_ingredients.measurement_unit_id = mu.id
        """
    )
    op.execute(
        """
        UPDATE shopping_list_items
        SET measurement_unit = mu.name
        FROM measurement_units mu
        WHERE shopping_list_items.measurement_unit_id = mu.id
        """
    )

    # Step 3: Drop foreign key constraints
    op.drop_constraint(
        "recipe_ingredients_measurement_unit_id_fkey",
        "recipe_ingredients",
        type_="foreignkey",
    )
    op.drop_constraint(
        "shopping_list_items_measurement_unit_id_fkey",
        "shopping_list_items",
        type_="foreignkey",
    )

    # Step 4: Drop old measurement_unit_id columns
    op.drop_column("recipe_ingredients", "measurement_unit_id")
    op.drop_column("shopping_list_items", "measurement_unit_id")

    # Step 5: Drop the measurement_units table
    op.drop_table("measurement_units")


def downgrade() -> None:
    # Recreate the measurement_units table
    op.create_table(
        "measurement_units",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("abbreviation", sa.String(50), nullable=True),
        sa.Column("system", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_measurement_units")),
        sa.UniqueConstraint("name", name="uq_measurement_units_name"),
    )

    # Re-add measurement_unit_id columns
    op.add_column(
        "recipe_ingredients",
        sa.Column("measurement_unit_id", sa.String(36), nullable=True),
    )
    op.add_column(
        "shopping_list_items",
        sa.Column("measurement_unit_id", sa.String(36), nullable=True),
    )

    # Re-create foreign key constraints
    op.create_foreign_key(
        "recipe_ingredients_measurement_unit_id_fkey",
        "recipe_ingredients",
        "measurement_units",
        ["measurement_unit_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "shopping_list_items_measurement_unit_id_fkey",
        "shopping_list_items",
        "measurement_units",
        ["measurement_unit_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Populate measurement_units from existing string values and set FK ids
    op.execute(
        """
        INSERT INTO measurement_units (id, name)
        SELECT DISTINCT gen_random_uuid(), measurement_unit
        FROM recipe_ingredients
        WHERE measurement_unit IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO measurement_units (id, name)
        SELECT DISTINCT gen_random_uuid(), measurement_unit
        FROM shopping_list_items
        WHERE measurement_unit IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        UPDATE recipe_ingredients
        SET measurement_unit_id = mu.id
        FROM measurement_units mu
        WHERE recipe_ingredients.measurement_unit = mu.name
        """
    )
    op.execute(
        """
        UPDATE shopping_list_items
        SET measurement_unit_id = mu.id
        FROM measurement_units mu
        WHERE shopping_list_items.measurement_unit = mu.name
        """
    )

    # Drop the string columns
    op.drop_column("recipe_ingredients", "measurement_unit")
    op.drop_column("shopping_list_items", "measurement_unit")
