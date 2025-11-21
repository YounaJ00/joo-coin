"""
데이터베이스 Enum 타입 정의
"""

from enum import Enum


class TradeType(str, Enum):
    """거래 타입"""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class RiskLevel(str, Enum):
    """위험 수준"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TradeStatus(str, Enum):
    """거래 상태"""

    PENDING = "pending"  # 진행 중
    SUCCESS = "success"  # 성공
    PARTIAL_SUCCESS = "partial_success"  # 부분 성공
    FAILED = "failed"  # 실패
    NO_ACTION = "no_action"  # 거래 없음 (코인 없음, 잔액 없음 등)
