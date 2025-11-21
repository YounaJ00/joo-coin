from typing import List

from pydantic import BaseModel

from app.upbit.dto.coin_balance import CoinBalance


class MyBallanceResponse(BaseModel):
    krw: float
    coin_balances: List[CoinBalance]
