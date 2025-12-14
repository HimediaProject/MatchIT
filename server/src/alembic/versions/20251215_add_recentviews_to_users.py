"""add recentviews to users

Revision ID: 20251215_add_recentviews
Revises: 20251212_add_experience_range
Create Date: 2025-12-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251215_add_recentviews"
down_revision: Union[str, None] = "20251212_add_experience_range"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("recentviews", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "recentviews")
