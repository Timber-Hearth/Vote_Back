"""add poll_id to votes

Revision ID: bce38e51d8a5
Revises: 36229430af65
Create Date: 2026-07-08 14:53:47.996868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bce38e51d8a5'
down_revision: Union[str, Sequence[str], None] = '36229430af65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('votes', sa.Column('poll_id', sa.UUID(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE votes
            SET poll_id = poll_options.poll_id
            FROM poll_options
            WHERE votes.option_id = poll_options.id
            """
        )
    )
    op.drop_index(op.f('ix_votes_poll_group_qr'), table_name='votes')
    op.drop_constraint(op.f('uq_votes_poll_anon_option'), 'votes', type_='unique')
    op.alter_column('votes', 'poll_id', existing_type=sa.UUID(), nullable=False)
    op.create_unique_constraint('uq_votes_poll_anon_option', 'votes', ['poll_id', 'anonymous_id', 'option_id'])
    op.create_index(op.f('ix_votes_poll_id'), 'votes', ['poll_id'], unique=False)
    op.drop_constraint(op.f('votes_poll_group_qr_fkey'), 'votes', type_='foreignkey')
    op.create_foreign_key('votes_poll_id_fkey', 'votes', 'poll', ['poll_id'], ['id'], ondelete='CASCADE')
    op.drop_column('votes', 'poll_group_qr')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('votes', sa.Column('poll_group_qr', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE votes
            SET poll_group_qr = poll_options.poll_group_qr
            FROM poll_options
            WHERE votes.option_id = poll_options.id
            """
        )
    )
    op.drop_constraint('votes_poll_id_fkey', 'votes', type_='foreignkey')
    op.create_foreign_key(op.f('votes_poll_group_qr_fkey'), 'votes', 'poll_group', ['poll_group_qr'], ['qr_token'], ondelete='CASCADE')
    op.drop_index(op.f('ix_votes_poll_id'), table_name='votes')
    op.drop_constraint('uq_votes_poll_anon_option', 'votes', type_='unique')
    op.alter_column('votes', 'poll_group_qr', existing_type=sa.VARCHAR(length=255), nullable=False)
    op.create_unique_constraint(op.f('uq_votes_poll_anon_option'), 'votes', ['poll_group_qr', 'anonymous_id', 'option_id'], postgresql_nulls_not_distinct=False)
    op.create_index(op.f('ix_votes_poll_group_qr'), 'votes', ['poll_group_qr'], unique=False)
    op.drop_column('votes', 'poll_id')
