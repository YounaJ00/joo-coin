"""
Balance Repository
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ballance.model.balance import Balance
from app.common.repository.base_repository import BaseRepository


class BalanceRepository(BaseRepository[Balance]):
    """Balance CRUD 연산"""

    def __init__(self, session: AsyncSession):
        super().__init__(Balance, session)

    async def get_latest(self) -> Optional[Balance]:
        """최신 잔고 조회"""
        result = await self.session.execute(
            select(Balance).order_by(Balance.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self, cursor: Optional[int] = None, limit: int = 20
    ) -> List[Balance]:
        """
        잔고 내역을 커서 기반 페이지네이션으로 조회

        @param cursor: 이전 페이지의 마지막 잔고 ID (None이면 첫 페이지)
        @param limit: 조회할 항목 수
        @return: 잔고 내역 목록
        """
        query = select(Balance).order_by(Balance.id.desc())

        if cursor is not None:
            query = query.where(Balance.id < cursor)

        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
