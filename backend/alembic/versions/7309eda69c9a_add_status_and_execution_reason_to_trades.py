"""add_status_and_execution_reason_to_trades

Revision ID: 7309eda69c9a
Revises: 9f321772914d
Create Date: 2025-11-22 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7309eda69c9a"
down_revision: Union[str, Sequence[str], None] = "9f321772914d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    trades 테이블에 거래 상태 추적을 위한 컬럼 추가:
    - status: 거래 상태 (PENDING, SUCCESS, PARTIAL_SUCCESS, FAILED)
    - execution_reason: 거래 실행 과정의 상세 로그
    """
    # status 컬럼 추가 (기존 데이터는 SUCCESS로 설정)
    op.add_column(
        "trades",
        sa.Column("status", sa.String(20), nullable=False, server_default="success"),
    )

    # execution_reason 컬럼 추가
    op.add_column("trades", sa.Column("execution_reason", sa.Text(), nullable=True))

    # server_default 제거 (기존 데이터 처리 후 불필요)
    op.alter_column("trades", "status", server_default=None)


def downgrade() -> None:
    """Downgrade schema.

    status, execution_reason 컬럼 제거
    """
    op.drop_column("trades", "execution_reason")
    op.drop_column("trades", "status")
