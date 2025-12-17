"""add experiencerangeid to users

Revision ID: 20251212_add_experience_range
Revises: 8f3c89db1300
Create Date: 2025-12-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "20251212_add_experience_range"
down_revision: Union[str, None] = "8f3c89db1300"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass

