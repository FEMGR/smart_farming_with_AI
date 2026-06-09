"""add plant identity growth facts and timeline snapshots

Revision ID: 7a4c19d8e2b1
Revises: 6f3a2b8c4d10
Create Date: 2026-06-02 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7a4c19d8e2b1"
down_revision: Union[str, Sequence[str], None] = "6f3a2b8c4d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.add_column("plants", sa.Column("plant_atom", sa.String(length=120), nullable=True))
    op.add_column("plants", sa.Column("scientific_name", sa.String(length=255), nullable=True))
    op.add_column("plants", sa.Column("genus", sa.String(length=120), nullable=True))
    op.add_column("plants", sa.Column("family", sa.String(length=120), nullable=True))
    op.add_column("plants", sa.Column("taxonomy_confidence", sa.String(length=50), nullable=True))
    op.create_index(op.f("ix_plants_plant_atom"), "plants", ["plant_atom"], unique=False)
    op.create_index(op.f("ix_plants_scientific_name"), "plants", ["scientific_name"], unique=False)
    op.create_index(op.f("ix_plants_genus"), "plants", ["genus"], unique=False)
    op.create_index(op.f("ix_plants_family"), "plants", ["family"], unique=False)

    op.create_table(
        "plant_growth_facts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plant_key", sa.String(length=120), nullable=False),
        sa.Column("scientific_name", sa.String(length=255), nullable=True),
        sa.Column("genus", sa.String(length=120), nullable=True),
        sa.Column("family", sa.String(length=120), nullable=True),
        sa.Column("germination_days_min", sa.Integer(), nullable=True),
        sa.Column("germination_days_max", sa.Integer(), nullable=True),
        sa.Column("germination_light", sa.String(length=80), nullable=True),
        sa.Column("stratification_required", sa.Boolean(), nullable=True),
        sa.Column("stratification_days_min", sa.Integer(), nullable=True),
        sa.Column("stratification_days_max", sa.Integer(), nullable=True),
        sa.Column("sowing_depth_cm", sa.Float(), nullable=True),
        sa.Column("minimum_soil_temp_c", sa.Float(), nullable=True),
        sa.Column("optimum_soil_temp_c", sa.Float(), nullable=True),
        sa.Column("viable_temp_min_c", sa.Float(), nullable=True),
        sa.Column("viable_temp_max_c", sa.Float(), nullable=True),
        sa.Column("special_treatments", json_type, nullable=True),
        sa.Column("source_names", json_type, nullable=True),
        sa.Column("source_urls", json_type, nullable=True),
        sa.Column("raw_facts", json_type, nullable=True),
        sa.Column("confidence", sa.String(length=50), nullable=True),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plant_key", name="uq_plant_growth_facts_plant_key"),
    )
    op.create_index(op.f("ix_plant_growth_facts_id"), "plant_growth_facts", ["id"], unique=False)
    op.create_index(op.f("ix_plant_growth_facts_plant_key"), "plant_growth_facts", ["plant_key"], unique=False)
    op.create_index(op.f("ix_plant_growth_facts_scientific_name"), "plant_growth_facts", ["scientific_name"], unique=False)
    op.create_index(op.f("ix_plant_growth_facts_genus"), "plant_growth_facts", ["genus"], unique=False)
    op.create_index(op.f("ix_plant_growth_facts_family"), "plant_growth_facts", ["family"], unique=False)

    op.create_table(
        "plant_timeline_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("growth_fact_id", sa.Integer(), nullable=True),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("basis", sa.String(length=80), nullable=False),
        sa.Column("timeline_data", json_type, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["growth_fact_id"], ["plant_growth_facts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plant_id", name="uq_plant_timeline_snapshots_plant_id"),
    )
    op.create_index(op.f("ix_plant_timeline_snapshots_id"), "plant_timeline_snapshots", ["id"], unique=False)
    op.create_index(op.f("ix_plant_timeline_snapshots_user_id"), "plant_timeline_snapshots", ["user_id"], unique=False)
    op.create_index(op.f("ix_plant_timeline_snapshots_plant_id"), "plant_timeline_snapshots", ["plant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_plant_timeline_snapshots_plant_id"), table_name="plant_timeline_snapshots")
    op.drop_index(op.f("ix_plant_timeline_snapshots_user_id"), table_name="plant_timeline_snapshots")
    op.drop_index(op.f("ix_plant_timeline_snapshots_id"), table_name="plant_timeline_snapshots")
    op.drop_table("plant_timeline_snapshots")

    op.drop_index(op.f("ix_plant_growth_facts_family"), table_name="plant_growth_facts")
    op.drop_index(op.f("ix_plant_growth_facts_genus"), table_name="plant_growth_facts")
    op.drop_index(op.f("ix_plant_growth_facts_scientific_name"), table_name="plant_growth_facts")
    op.drop_index(op.f("ix_plant_growth_facts_plant_key"), table_name="plant_growth_facts")
    op.drop_index(op.f("ix_plant_growth_facts_id"), table_name="plant_growth_facts")
    op.drop_table("plant_growth_facts")

    op.drop_index(op.f("ix_plants_family"), table_name="plants")
    op.drop_index(op.f("ix_plants_genus"), table_name="plants")
    op.drop_index(op.f("ix_plants_scientific_name"), table_name="plants")
    op.drop_index(op.f("ix_plants_plant_atom"), table_name="plants")
    op.drop_column("plants", "taxonomy_confidence")
    op.drop_column("plants", "family")
    op.drop_column("plants", "genus")
    op.drop_column("plants", "scientific_name")
    op.drop_column("plants", "plant_atom")
