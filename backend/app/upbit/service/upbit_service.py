from app.upbit.client.upbit_client import UpbitClient
from app.upbit.dto.ohlcv_dto import OhlcvItem


class UpbitService:
    def __init__(self):
        self.upbit_client = UpbitClient()

    async def get_ohlcv(self, coin_name: str) -> OhlcvItem:
        return await self.upbit_client.get_ohlcv(coin_name)
