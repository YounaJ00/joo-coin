from sqlalchemy.ext.asyncio import AsyncSession

from app.coin.service.coin_service import CoinService
from app.trade.repository.trade_repository import TradeRepository
from app.upbit.client import upbit_client


class TradeService:
    def __init__(self, session: AsyncSession):
        self.trade_repository = TradeRepository(session)
        self.coin_service = CoinService(session=session)
        self.upbit_service = UpbitService(session=session)

    async def execute(self):
        df = self.upbit_service.get
