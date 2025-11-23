"""
Trade Repository
"""

from typing import List, Optional

from app.common.repository.base_repository import BaseRepository
from app.trade.model.trade import Trade
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class TradeRepository(BaseRepository[Trade]):
    """Trade CRUD 연산"""

    def __init__(self, session: AsyncSession):
        super().__init__(Trade, session)

    async def get_by_coin_id(self, coin_id: int) -> List[Trade]:
        """코인 ID로 거래 내역 조회"""
        result = await self.session.execute(
            select(Trade)
            .where(Trade.coin_id == coin_id)
            .order_by(Trade.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_with_coin(self) -> List[Trade]:
        """
        모든 거래 내역을 코인 정보와 함께 조회

        @return: 생성 시각 기준 내림차순으로 정렬된 거래 내역 목록
        """
        result = await self.session.execute(
            select(Trade)
            .options(selectinload(Trade.coin))
            .order_by(Trade.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_with_coin_paginated(
        self, cursor: Optional[int], limit: int, trade_type: Optional[str]
    ) -> List[Trade]:
        """
        거래 내역을 커서 기반 페이지네이션으로 조회

        @param cursor: 이전 페이지의 마지막 거래 ID (None이면 첫 페이지)
        @param limit: 조회할 최대 개수
        @return: 생성 시각 기준 내림차순으로 정렬된 거래 내역 목록
        """
        query = select(Trade).options(selectinload(Trade.coin))

        # cursor가 있으면 해당 ID보다 작은 항목만 조회
        if cursor is not None:
            query = query.where(Trade.id < cursor)

        if trade_type is not None:
            query = query.where(Trade.trade_type == trade_type)

        # created_at 기준 내림차순 정렬
        query = query.order_by(Trade.created_at.desc()).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())
