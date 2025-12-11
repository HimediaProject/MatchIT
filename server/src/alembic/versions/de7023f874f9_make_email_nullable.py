"""make email nullable

Revision ID: de7023f874f9
Revises: 8f3c89db1300
Create Date: 2025-12-08 07:25:36.037801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'de7023f874f9'
down_revision: Union[str, None] = '8f3c89db1300'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        'users', 
        'email',
        existing_type=sa.String(length=255),
        nullable=True
    )

def downgrade() -> None:
    op.alter_column(
        'users', 
        'email',
        existing_type=sa.String(length=255),
        nullable=False
    )