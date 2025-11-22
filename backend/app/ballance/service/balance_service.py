"""
Balance Service
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ballance.dto.balance_response import BalanceItemResponse, BalancesResponse
from app.ballance.repository.balance_repository import BalanceRepository


class BalanceService:
    """잔고 비즈니스 로직"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.balance_repository = BalanceRepository(session)

    async def get_balances(
        self, cursor: Optional[int] = None, limit: int = 20
    ) -> BalancesResponse:
        """
        잔고 내역을 커서 기반 페이지네이션으로 조회

        @param cursor: 이전 페이지의 마지막 잔고 ID (None이면 첫 페이지)
        @param limit: 페이지당 조회할 항목 수 (기본: 20)
        @return: 잔고 내역 목록 응답 (다음 페이지 정보 포함)
        """
        # limit + 1개를 조회하여 다음 페이지 존재 여부 확인
        balances = await self.balance_repository.get_all_paginated(
            cursor=cursor, limit=limit + 1
        )

        # 다음 페이지 존재 여부 판단
        has_next = len(balances) > limit

        # 실제 반환할 항목은 limit개만
        if has_next:
            balances = balances[:limit]
            next_cursor = balances[-1].id if balances else None
        else:
            next_cursor = None

        items = [BalanceItemResponse.from_balance(balance) for balance in balances]

        return BalancesResponse(
            items=items, next_cursor=next_cursor, has_next=has_next
        )
