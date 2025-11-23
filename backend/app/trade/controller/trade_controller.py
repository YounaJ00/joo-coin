from typing import Optional

from app.common.model.base import get_session
from app.trade.dto.transaction_response import TransactionsResponse
from app.trade.service.trade_service import TradeService
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

trade_router = APIRouter(prefix="/trade", tags=["Trade"])


@trade_router.post(
    "",
    summary="즉시 트레이드 실행",
    description="등록 해놓은 코인을 기반으로 즉시 트레이드를 실행합니다.",
)
async def execute_trades(session: AsyncSession = Depends(get_session)) -> None:
    """트레이드 실행 엔드포인트"""
    trade_service = TradeService(session)
    await trade_service.execute()


@trade_router.get(
    "/transactions",
    summary="내 거래 내역 조회",
    description="내 거래 내역을 최신순으로 페이지네이션하여 반환합니다.",
    response_model=TransactionsResponse,
)
async def get_transactions(
    cursor: Optional[int] = Query(
        None,
        description="이전 페이지의 마지막 거래 ID (첫 페이지 조회 시 생략)",
    ),
    trade_type: Optional[str] = Query(
        None,
        description="거래 유형 필터 (예: 'buy', 'sell', 'hold)",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="페이지당 조회할 항목 수 (1-100, 기본값: 20)",
    ),
    session: AsyncSession = Depends(get_session),
) -> TransactionsResponse:
    """
    내 거래 내역 조회 (Cursor 기반 페이지네이션)

    거래 내역을 최신순으로 페이지네이션하여 반환합니다.

    **사용 방법:**
    1. 첫 페이지: `GET /transactions?limit=20`
    2. 다음 페이지: 응답의 `next_cursor` 값을 사용하여 `GET /transactions?cursor={next_cursor}&limit=20`
    3. `has_next`가 `false`이면 마지막 페이지

    **각 거래 항목 정보:**
    - 코인 정보 (ID, 이름)
    - 거래 유형 (buy/sell)
    - 거래 가격 및 수량
    - 위험도 (none/low/medium/high)
    - 거래 상태 (pending/success/partial_success/failed/no_action)
    - AI 분석 결과 (ai_reason)
    - 거래 실행 사유 (execution_reason): 잔고, 현재 가격, 수수료, 실패 원인 등 상세 정보
    """
    trade_service = TradeService(session)
    return await trade_service.get_transactions(
        cursor=cursor, limit=limit, trade_type=trade_type
    )
