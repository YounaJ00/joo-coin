"""
Coin API Controller
"""

from fastapi import APIRouter, Depends, status

from app.coin.dto.coin_dto import CoinListResponse, CoinResponse, CreateCoinRequest
from app.coin.service.coin_service import CoinService

coin_router = APIRouter(prefix="/my/coins", tags=["My Coin"])


@coin_router.get(
    "",
    response_model=CoinListResponse,
    summary="내 거래 코인 조회",
    description="내 거래 코인 목록을 조회합니다.",
)
async def get_my_coins(
    service: CoinService = Depends(),
) -> CoinListResponse:
    """내 거래 코인 목록 조회"""
    coins = await service.get_all_active()
    return CoinListResponse(items=[CoinResponse.model_validate(coin) for coin in coins])


@coin_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="거래 코인 추가",
    description="새로운 거래 코인을 추가합니다. 이미 삭제된 코인이 있으면 복구합니다.",
)
async def create_coin(
    request: CreateCoinRequest,
    service: CoinService = Depends(),
) -> None:
    """거래 코인 추가"""
    await service.create_coin(request.name)


@coin_router.delete(
    "/{coin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="내 코인 정보 삭제",
    description="코인을 soft delete 합니다.",
)
async def delete_coin(
    coin_id: int,
    service: CoinService = Depends(),
) -> None:
    """코인 soft delete"""
    await service.delete_coin(coin_id)
