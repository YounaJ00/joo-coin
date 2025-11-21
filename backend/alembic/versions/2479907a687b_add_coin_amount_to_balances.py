"""add_coin_amount_to_balances

Revision ID: 2479907a687b
Revises: 7cf1639cbeec
Create Date: 2025-11-21 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2479907a687b'
down_revision: Union[str, Sequence[str], None] = '7cf1639cbeec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('balances', sa.Column('coin_amount', sa.Numeric(20, 8), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('balances', 'coin_amount')
