"""
Balance Response DTO
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class BalanceItemResponse(BaseModel):
    """잔고 내역 항목 응답 DTO"""

    id: int = Field(description="잔고 기록 ID")
    amount: float = Field(description="KRW 잔고")
    coin_amount: float = Field(description="코인 보유량 (KRW 가치)")
    total_amount: float = Field(description="총 자산 (KRW + 코인)")
    created_at: str = Field(description="기록 시각 (YYYY-MM-DD HH:MM:SS)")

    @staticmethod
    def from_balance(balance) -> "BalanceItemResponse":
        """Balance 엔티티를 BalanceItemResponse로 변환"""
        amount = float(balance.amount) if isinstance(balance.amount, Decimal) else balance.amount
        coin_amount = float(balance.coin_amount) if isinstance(balance.coin_amount, Decimal) else balance.coin_amount

        return BalanceItemResponse(
            id=balance.id,
            amount=amount,
            coin_amount=coin_amount,
            total_amount=amount + coin_amount,
            created_at=balance.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(balance.created_at, datetime) else balance.created_at,
        )


class BalancesResponse(BaseModel):
    """잔고 내역 목록 응답 DTO (Cursor 기반 페이지네이션)"""

    items: list[BalanceItemResponse] = Field(description="잔고 내역 목록")
    next_cursor: Optional[int] = Field(
        description="다음 페이지를 조회하기 위한 커서 (다음 페이지가 없으면 null)"
    )
    has_next: bool = Field(description="다음 페이지 존재 여부")
