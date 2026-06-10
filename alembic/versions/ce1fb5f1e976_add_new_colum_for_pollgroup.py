"""Add new Colum for PollGroup

Revision ID: ce1fb5f1e976
Revises: 998231a6cfcf
Create Date: 2026-06-10 09:32:45.148651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce1fb5f1e976'
down_revision: Union[str, Sequence[str], None] = '998231a6cfcf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
