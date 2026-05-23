"""add plant bed position

Revision ID: c9d3e7f1a204
Revises: b7c2d4e9f101
Create Date: 2026-05-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9d3e7f1a204"
down_revision: Union[str, Sequence[str], None] = "b7c2d4e9f101"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("plants", sa.Column("bed_x", sa.Integer(), nullable=True))
    op.add_column("plants", sa.Column("bed_y", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("plants", "bed_y")
    op.drop_column("plants", "bed_x")
