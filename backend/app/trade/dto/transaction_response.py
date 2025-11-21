"""
Transaction Response DTO
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class TransactionItemResponse(BaseModel):
    """거래 내역 항목 응답 DTO"""

    id: int = Field(description="거래 ID")
    coin_id: Optional[int] = Field(description="코인 ID")
    coin_name: Optional[str] = Field(description="코인 이름")
    type: Optional[str] = Field(description="거래 타입 (buy/sell)")
    price: float = Field(description="거래 가격")
    amount: float = Field(description="거래 수량")
    risk_level: str = Field(description="위험 수준 (none/low/medium/high)")
    status: str = Field(description="거래 상태 (pending/success/partial_success/failed/no_action)")
    timestamp: str = Field(description="거래 시각 (YYYY-MM-DD HH:MM:SS)")
    ai_reason: Optional[str] = Field(description="AI 분석 결과")
    execution_reason: Optional[str] = Field(description="거래 실행 사유 (잔고, 가격, 수량 등 상세 정보)")

    @staticmethod
    def from_trade(trade, coin_name: Optional[str] = None) -> "TransactionItemResponse":
        """Trade 엔티티를 TransactionItemResponse로 변환"""
        return TransactionItemResponse(
            id=trade.id,
            coin_id=trade.coin_id,
            coin_name=coin_name,
            type=trade.trade_type,
            price=float(trade.price) if isinstance(trade.price, Decimal) else trade.price,
            amount=float(trade.amount) if isinstance(trade.amount, Decimal) else trade.amount,
            risk_level=trade.risk_level,
            status=trade.status,
            timestamp=trade.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(trade.created_at, datetime) else trade.created_at,
            ai_reason=trade.ai_reason,
            execution_reason=trade.execution_reason,
        )


class TransactionsResponse(BaseModel):
    """거래 내역 목록 응답 DTO"""

    items: list[TransactionItemResponse] = Field(description="거래 내역 목록")
