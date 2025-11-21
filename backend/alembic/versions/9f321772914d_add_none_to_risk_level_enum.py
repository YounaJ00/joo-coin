"""add_none_to_risk_level_enum

Revision ID: 9f321772914d
Revises: 2479907a687b
Create Date: 2025-11-21 22:51:32.187015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f321772914d'
down_revision: Union[str, Sequence[str], None] = '2479907a687b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    RiskLevel enum에 'none' 값 추가
    - 기존: LOW, MEDIUM, HIGH
    - 추가: NONE (ai_analysis_response.py와 동기화)

    trades 테이블의 risk_level 컬럼은 VARCHAR(10)이므로
    DB 스키마 변경 없이 새 값 저장 가능
    """
    # VARCHAR 타입이므로 실제 DB 스키마 변경 불필요
    # Python enum 코드 변경만 필요:
    # app/trade/model/enums.py의 RiskLevel에 NONE = "none" 추가
    pass


def downgrade() -> None:
    """Downgrade schema.

    RiskLevel enum에서 'none' 값 제거
    주의: 기존 데이터에 'none' 값이 있으면 애플리케이션 오류 발생 가능
    """
    # 기존 'none' 데이터를 다른 값으로 변환해야 할 경우:
    # op.execute("UPDATE trades SET risk_level = 'low' WHERE risk_level = 'none'")
    pass
