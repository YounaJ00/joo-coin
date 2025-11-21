"""
Trade Repository
"""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.repository.base_repository import BaseRepository
from app.trade.model.trade import Trade


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
