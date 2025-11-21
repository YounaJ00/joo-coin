from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Decision(str, Enum):
    """AI 분석 결과 결정 유형"""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class RiskLevel(str, Enum):
    """리스크 수준"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AiAnalysisResponse(BaseModel):
    """AI 비트코인 분석 결과 DTO"""

    decision: Decision = Field(description="투자 결정 (buy/sell/hold)")
    confidence: float = Field(ge=0, le=1, description="신뢰도 (0~1)")
    reason: str = Field(description="분석 근거")
    risk_level: RiskLevel = Field(description="리스크 수준")
    timestamp: datetime = Field(description="분석 시점")
