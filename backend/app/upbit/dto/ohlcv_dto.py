"""
OHLCV DTO
"""

from datetime import datetime

from pydantic import BaseModel, Field


class OhlcvItem(BaseModel):
    """단일 OHLCV 데이터"""

    timestamp: datetime = Field(description="시간")
    open: float = Field(description="시가")
    high: float = Field(description="고가")
    low: float = Field(description="저가")
    close: float = Field(description="종가")
    volume: float = Field(description="거래량")
    value: float = Field(description="거래대금")


class OhlcvResponse(BaseModel):
    """OHLCV 응답 DTO"""

    items: list[OhlcvItem] = Field(description="OHLCV 데이터 목록")
