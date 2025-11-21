"""
Balance Repository
"""

from typing import Optional

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
