"""Add new Colum for PollGroup

Revision ID: 998231a6cfcf
Revises: 113c250468f2
Create Date: 2026-06-10 09:30:20.877500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '998231a6cfcf'
down_revision: Union[str, Sequence[str], None] = '113c250468f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
