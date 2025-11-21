"""add_is_deleted_to_coins

Revision ID: 7cf1639cbeec
Revises: a5618c7dd872
Create Date: 2025-11-21 21:29:47.231697

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7cf1639cbeec"
down_revision: Union[str, Sequence[str], None] = "a5618c7dd872"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "coins",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("coins", "is_deleted")
