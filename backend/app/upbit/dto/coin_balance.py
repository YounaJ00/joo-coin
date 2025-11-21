from openai import BaseModel


class CoinBalance(BaseModel):
    coin_name: str
    balance: float
