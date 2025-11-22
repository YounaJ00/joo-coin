"""
Balance Controller
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.ballance.dto.balance_response import BalancesResponse
from app.ballance.service.balance_service import BalanceService
from app.common.model.base import get_session

balance_router = APIRouter(prefix="/balance", tags=["Balance"])


@balance_router.get(
    "/history",
    summary="잔고 변화 내역 조회",
    description="잔고 변화 내역을 최신순으로 페이지네이션하여 반환합니다.",
    response_model=BalancesResponse,
)
async def get_balance_history(
    cursor: Optional[int] = Query(
        None,
        description="이전 페이지의 마지막 잔고 ID (첫 페이지 조회 시 생략)",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="페이지당 조회할 항목 수 (1-100, 기본값: 20)",
    ),
    session: AsyncSession = Depends(get_session),
) -> BalancesResponse:
    """
    잔고 변화 내역 조회 (Cursor 기반 페이지네이션)

    잔고 변화 내역을 최신순으로 페이지네이션하여 반환합니다.

    **사용 방법:**
    1. 첫 페이지: `GET /balance/history?limit=20`
    2. 다음 페이지: 응답의 `next_cursor` 값을 사용하여 `GET /balance/history?cursor={next_cursor}&limit=20`
    3. `has_next`가 `false`이면 마지막 페이지

    **각 잔고 항목 정보:**
    - KRW 잔고
    - 코인 보유량 (KRW 가치로 환산)
    - 총 자산 (KRW + 코인)
    - 기록 시각
    """
    balance_service = BalanceService(session)
    return await balance_service.get_balances(cursor=cursor, limit=limit)
