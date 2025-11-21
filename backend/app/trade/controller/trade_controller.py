from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.model.base import get_session
from app.trade.dto.transaction_response import TransactionsResponse
from app.trade.service.trade_service import TradeService

trade_router = APIRouter(prefix="/trade", tags=["Trade"])


@trade_router.post("")
async def execute_trades(session: AsyncSession = Depends(get_session)) -> None:
    """트레이드 실행 엔드포인트"""
    trade_service = TradeService(session)
    await trade_service.execute()


@trade_router.get("/transactions")
async def get_transactions(
    session: AsyncSession = Depends(get_session),
) -> TransactionsResponse:
    """
    내 거래 내역 조회

    모든 거래 내역을 최신순으로 반환합니다.
    각 거래 항목에는 다음 정보가 포함됩니다:
    - 코인 정보 (ID, 이름)
    - 거래 유형 (buy/sell)
    - 거래 가격 및 수량
    - 위험도 (none/low/medium/high)
    - 거래 상태 (pending/success/partial_success/failed/no_action)
    - AI 분석 결과 (ai_reason)
    - 거래 실행 사유 (execution_reason): 잔고, 현재 가격, 수수료, 실패 원인 등 상세 정보
    """
    trade_service = TradeService(session)
    return await trade_service.get_transactions()
