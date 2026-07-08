"""restore missing revision

Revision ID: 36229430af65
Revises: d6a221e4a9c6
Create Date: 2026-07-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36229430af65'
down_revision: Union[str, Sequence[str], None] = 'd6a221e4a9c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Restore a missing revision file so Alembic history matches the DB."""
    pass


def downgrade() -> None:
    """No-op downgrade because the original revision contents are unavailable."""
    pass