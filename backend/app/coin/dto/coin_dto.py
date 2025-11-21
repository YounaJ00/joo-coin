"""
Coin DTO
"""

from pydantic import BaseModel, Field


class CoinResponse(BaseModel):
    """코인 응답 DTO"""

    id: int = Field(description="코인 ID")
    name: str = Field(description="코인 이름")

    class Config:
        from_attributes = True


class CoinListResponse(BaseModel):
    """코인 목록 응답 DTO"""

    items: list[CoinResponse] = Field(description="코인 목록")


class CreateCoinRequest(BaseModel):
    """코인 생성 요청 DTO"""

    name: str = Field(description="코인 이름", min_length=1, max_length=100)
