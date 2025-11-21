from fastapi import APIRouter, Depends

from app.upbit.service.upbit_service import UpbitService

upbit_router = APIRouter(prefix="/coins", tags=["Upbit"])


@upbit_router.get(
    "/{coin_name}",
    description="특정 코인의 OHLCV 데이터를 Upbit로부터 조회합니다. 500 Internal Server Error 발생 시 해당 코인이 존재하지 않는 것으로 간주합니다.",
    summary="코인 OHLCV 조회",
    responses={
        500: {
            "description": "해당 코인이 존재하지 않거나 Upbit API 호출 실패. 코인이 없는 것으로 간주하세요.",
        }
    },
)
async def trade_coin(
    coin_name: str, upbit_service: UpbitService = Depends(UpbitService)
):
    return await upbit_service.get_ohlcv(coin_name)
