"""
데이터베이스 Enum 타입 정의
"""

from enum import Enum


class TradeType(str, Enum):
    """거래 타입"""

    BUY = "buy"
    SELL = "sell"


class RiskLevel(str, Enum):
    """위험 수준"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
