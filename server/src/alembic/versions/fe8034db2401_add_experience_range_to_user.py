"""add experience_range_to_user

Revision ID: fe8034db2401
Revises: de7023f874f9
Create Date: 2025-12-11 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe8034db2401'
down_revision: Union[str, None] = 'de7023f874f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # experiencerangeid 컬럼 추가
    op.add_column('users', sa.Column('experiencerangeid', sa.Integer(), nullable=True))
    
    # Foreign Key 제약 추가
    op.create_foreign_key(
        'fk_users_experiencerangeid',
        'users', 'experienceranges',
        ['experiencerangeid'], ['rangeid']
    )


def downgrade() -> None:
    # Foreign Key 제약 제거
    op.drop_constraint('fk_users_experiencerangeid', 'users', type_='foreignkey')
    
    # 컬럼 제거
    op.drop_column('users', 'experiencerangeid')
