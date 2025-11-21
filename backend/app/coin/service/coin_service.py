"""
Coin Service
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.coin.model.coin import Coin
from app.coin.repository.coin_repository import CoinRepository
from app.common.model.base import get_session
from app.upbit.client.upbit_client import (
    UpbitClient,  # noqa: F401 - relationship 등록용
)


class CoinService:
    """코인 비즈니스 로직"""

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.repository = CoinRepository(session)
        self.upbit_client = UpbitClient()

    async def get_all_active(self) -> list[Coin]:
        """삭제되지 않은 모든 코인 조회"""
        return await self.repository.get_all_active()

    async def create_coin(self, name: str) -> None:
        """
        코인 생성 또는 복구

        Args:
            name: 코인 이름

        Raises:
            HTTPException: 이미 존재하는 코인인 경우
        """
        existing_coin = await self.repository.get_by_name_include_deleted(name)

        if existing_coin:
            if not existing_coin.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"이미 존재하는 코인입니다: {name}",
                )
            # soft delete된 코인 복구
            existing_coin.is_deleted = False
            await self.repository.update(existing_coin)
        else:
            # 새 코인 생성
            new_coin = Coin(name=name)
            await self.repository.create(new_coin)

    async def delete_coin(self, coin_id: int) -> None:
        """
        코인 soft delete

        Args:
            coin_id: 코인 ID

        Raises:
            HTTPException: 코인을 찾을 수 없는 경우
        """
        coin = await self.repository.get_by_id(coin_id)
        amount = self.upbit_client.get_krw_balance(coin.name) or 0.0

        if amount > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="잔고가 남아있는 코인은 삭제할 수 없습니다.",
            )

        if not coin or coin.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="코인을 찾을 수 없습니다.",
            )

        coin.is_deleted = True
        await self.repository.update(coin)
