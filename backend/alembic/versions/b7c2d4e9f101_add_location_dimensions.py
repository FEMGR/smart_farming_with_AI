"""add location dimensions

Revision ID: b7c2d4e9f101
Revises: 55d5000e19f8
Create Date: 2026-05-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c2d4e9f101"
down_revision: Union[str, Sequence[str], None] = "55d5000e19f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("locations", sa.Column("width_m", sa.Numeric(8, 2), nullable=True))
    op.add_column("locations", sa.Column("length_m", sa.Numeric(8, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("locations", "length_m")
    op.drop_column("locations", "width_m")
