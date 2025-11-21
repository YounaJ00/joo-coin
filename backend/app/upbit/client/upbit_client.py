from typing import List

import pyupbit
from pandas import DataFrame

from app.configs import config
from app.upbit.dto.coin_balance import CoinBalance
from app.upbit.dto.my_ballance_response import MyBallanceResponse
from app.upbit.dto.ohlcv_dto import OhlcvItem, OhlcvResponse


class UpbitClient:
    def __init__(self):
        self.access = config.Settings().UPBIT_ACCESS_KEY
        self.secret = config.Settings().UPBIT_SECRET_KEY
        self.upbit = pyupbit.Upbit(self.access, self.secret)

    # 시세 조회 API
    def get_ohlcv(self, coin_name: str) -> OhlcvResponse:
        """
        OHLCV 데이터를 조회합니다.

        @param coin_name: 티커 (예: "KRW-BTC")
        @return: OhlcvResponse
        @raises ValueError: 유효하지 않은 티커이거나 데이터 조회 실패 시
        """
        df: DataFrame = pyupbit.get_ohlcv(coin_name)

        if df is None:
            raise ValueError(
                f"'{coin_name}' 데이터를 조회할 수 없습니다. 티커 형식을 확인하세요 (예: KRW-BTC)"
            )

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

    # 시세 조회 API
    def get_ohlcv_raw(self, coin_name: str) -> DataFrame:
        """
        OHLCV 데이터를 조회합니다.

        @param coin_name: 티커 (예: "KRW-BTC")
        @return: OhlcvResponse
        @raises ValueError: 유효하지 않은 티커이거나 데이터 조회 실패 시
        """
        df: DataFrame = pyupbit.get_ohlcv(coin_name)

        if df is None:
            raise ValueError(
                f"'{coin_name}' 데이터를 조회할 수 없습니다. 티커 형식을 확인하세요 (예: KRW-BTC)"
            )

        return df

    def get_current_price(self, coin_name: str) -> float:
        # 현재 매도 호가 조회
        orderbook = pyupbit.get_orderbook(ticker=coin_name)
        current_price = orderbook["orderbook_units"][0]["ask_price"]
        return current_price

    def buy(self, coin_name: str, amount: float) -> None:
        self.upbit.buy_market_order(coin_name, amount)

    def sell(self, coin_name: str, amount: float) -> None:
        """
        코인 시장가 매도를 실행합니다.

        @param coin_name: 티커 (예: "KRW-BTC")
        @param amount: 매도할 코인 수량
        """
        self.upbit.sell_market_order(coin_name, amount)

    def get_coin_balance(self, coin_name: str) -> float:
        """
        특정 코인의 보유량을 조회합니다.

        @param coin_name: 티커 (예: "KRW-BTC")
        @return: 보유 코인 수량 (없으면 0.0)
        """
        balance = self.upbit.get_balance(coin_name)
        return balance if balance is not None else 0.0

    def get_krw_balance(self) -> float:
        """
        KRW 잔고를 조회합니다.

        @return: KRW 잔고 (없으면 0.0)
        """
        balance = self.upbit.get_balance("KRW")
        return balance if balance is not None else 0.0

    def get_my_balance(self, coin_names: list[str]) -> MyBallanceResponse:
        krw = self.upbit.get_balance("KRW") or 0.0
        coin_balaces: List[CoinBalance] = []
        for coin in coin_names:
            balance = self.upbit.get_balance(coin) or 0.0
            coin_balaces.append(CoinBalance(coin_name=coin, balance=balance))

        return MyBallanceResponse(krw=krw, coin_balances=coin_balaces)
