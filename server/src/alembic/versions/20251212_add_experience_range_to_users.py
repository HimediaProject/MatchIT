"""add experiencerangeid to users

Revision ID: 20251212_add_experience_range
Revises: 8f3c89db1300
Create Date: 2025-12-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20251212_add_experience_range"
down_revision: Union[str, None] = "8f3c89db1300"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("experiencerangeid", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_users_experiencerange",
        "users",
        "experienceranges",
        ["experiencerangeid"],
        ["rangeid"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_experiencerange", "users", type_="foreignkey")
    op.drop_column("users", "experiencerangeid")

