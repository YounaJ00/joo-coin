import pyupbit

from app.configs import config
from app.upbit.dto.ohlcv_dto import OhlcvItem, OhlcvResponse


class UpbitClient:
    def __init__(self):
        self.access = config.Settings().UPBIT_ACCESS_KEY
        self.secret = config.Settings().UPBIT_SECRET_KEY

    # 시세 조회 API
    async def get_ohlcv(self, coin_name: str) -> OhlcvResponse:
        df = pyupbit.get_ohlcv(coin_name)

        items = [
            OhlcvItem(
                timestamp=index.to_pydatetime(),
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
                value=row["value"],
            )
            for index, row in df.iterrows()
        ]

        return OhlcvResponse(items=items)
