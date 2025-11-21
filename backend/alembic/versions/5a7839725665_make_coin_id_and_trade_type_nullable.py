"""make_coin_id_and_trade_type_nullable

Revision ID: 5a7839725665
Revises: 7309eda69c9a
Create Date: 2025-11-22 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a7839725665'
down_revision: Union[str, Sequence[str], None] = '7309eda69c9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.
    
    trades 테이블의 coin_id와 trade_type을 nullable로 변경
    - 전체 실행 상황(코인 없음, 잔액 없음 등)을 기록하기 위함
    - price, amount는 기본값 0 사용
    - risk_level은 기본값 'none' 사용
    """
    # coin_id를 nullable로 변경
    op.alter_column(
        'trades',
        'coin_id',
        existing_type=sa.BigInteger(),
        nullable=True
    )
    
    # trade_type을 nullable로 변경
    op.alter_column(
        'trades',
        'trade_type',
        existing_type=sa.String(10),
        nullable=True
    )


def downgrade() -> None:
    """Downgrade schema.
    
    coin_id와 trade_type을 다시 NOT NULL로 변경
    주의: NULL 값이 있는 레코드가 있으면 실패함
    """
    # NULL 값을 가진 레코드 삭제 또는 기본값 설정 필요
    # op.execute("DELETE FROM trades WHERE coin_id IS NULL OR trade_type IS NULL")
    
    op.alter_column(
        'trades',
        'trade_type',
        existing_type=sa.String(10),
        nullable=False
    )
    
    op.alter_column(
        'trades',
        'coin_id',
        existing_type=sa.BigInteger(),
        nullable=False
    )
