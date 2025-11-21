"""
Trade Repository
"""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.trade import Trade
from app.database.repositories.base_repository import BaseRepository


class TradeRepository(BaseRepository[Trade]):
    """Trade CRUD 연산"""

    def __init__(self, session: AsyncSession):
        super().__init__(Trade, session)

    async def get_by_coin_id(self, coin_id: int) -> List[Trade]:
        """코인 ID로 거래 내역 조회"""
        result = await self.session.execute(
            select(Trade).where(Trade.coin_id == coin_id).order_by(Trade.created_at.desc())
        )
        return list(result.scalars().all())
