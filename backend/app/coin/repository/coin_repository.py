"""
Coin Repository
"""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.coin.model.coin import Coin
from app.common.repository.base_repository import BaseRepository


class CoinRepository(BaseRepository[Coin]):
    """Coin CRUD 연산"""

    def __init__(self, session: AsyncSession):
        super().__init__(Coin, session)

    async def get_by_name(self, name: str) -> Optional[Coin]:
        """이름으로 코인 조회"""
        result = await self.session.execute(select(Coin).where(Coin.name == name))
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Coin]:
        """삭제되지 않은 모든 코인 조회"""
        result = await self.session.execute(
            select(Coin).where(Coin.is_deleted == False)  # noqa: E712
        )
        return list(result.scalars().all())

    async def get_by_name_include_deleted(self, name: str) -> Optional[Coin]:
        """이름으로 코인 조회 (soft delete 포함)"""
        result = await self.session.execute(select(Coin).where(Coin.name == name))
        return result.scalar_one_or_none()

    async def get_all_include_deleted(self) -> Sequence[Coin]:
        """이름으로 코인 조회 (soft delete 포함)"""
        result = await self.session.execute(select(Coin))
        return result.scalars().all()
