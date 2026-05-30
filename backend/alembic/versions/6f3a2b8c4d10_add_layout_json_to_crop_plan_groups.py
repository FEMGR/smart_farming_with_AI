"""add layout json to crop plan groups

Revision ID: 6f3a2b8c4d10
Revises: 2b35d0fed869
Create Date: 2026-05-30 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f3a2b8c4d10"
down_revision: Union[str, Sequence[str], None] = "2b35d0fed869"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("crop_plan_groups", sa.Column("layout_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("crop_plan_groups", "layout_json")
