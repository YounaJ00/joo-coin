from fastapi import APIRouter, Depends

from app.upbit.client.upbit_client import UpbitClient
from app.upbit.di.upbit_di import get_upbit_client
from app.upbit.dto.ohlcv_dto import OhlcvResponse

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
def trade_coin(
    coin_name: str, upbit_client: UpbitClient = Depends(get_upbit_client)
) -> OhlcvResponse:
    return upbit_client.get_ohlcv(coin_name)
