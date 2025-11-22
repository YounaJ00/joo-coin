"""
MySQL Named Lock 유틸리티

여러 워커에서 동시 실행을 방지하기 위한 분산 락을 제공합니다.
MySQL의 GET_LOCK/RELEASE_LOCK 함수를 사용합니다.
"""

from contextlib import asynccontextmanager
from logging import Logger
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.model.base import get_session_maker

logger = Logger(__name__)


@asynccontextmanager
async def named_lock(
    lock_name: str,
    timeout: int = 0,
) -> AsyncGenerator[bool, None]:
    """
    MySQL Named Lock 컨텍스트 매니저

    @param lock_name: 락 이름 (고유 식별자)
    @param timeout: 락 획득 대기 시간 (초, 기본: 0 - 즉시 반환)
    @return: 락 획득 성공 여부

    사용 예시:
        async with named_lock("trade_execution") as acquired:
            if acquired:
                # 락 획득 성공 - 작업 실행
                await do_work()
            else:
                # 락 획득 실패 - 다른 워커가 실행 중
                pass
    """
    session_maker = get_session_maker()
    acquired = False

    # Named Lock은 세션 레벨이므로 별도 세션 사용
    async with session_maker() as session:
        try:
            # GET_LOCK(name, timeout) - 락 획득 시도
            # 반환값: 1 (성공), 0 (타임아웃), NULL (에러)
            result = await session.execute(
                text("SELECT GET_LOCK(:lock_name, :timeout)"),
                {"lock_name": lock_name, "timeout": timeout},
            )
            lock_result = result.scalar()
            acquired = lock_result == 1

            if acquired:
                logger.info(f"락 획득 성공: {lock_name}")
            else:
                logger.info(f"락 획득 실패: {lock_name} (다른 워커가 실행 중)")

            yield acquired

        finally:
            # 락을 획득한 경우에만 해제
            if acquired:
                await session.execute(
                    text("SELECT RELEASE_LOCK(:lock_name)"),
                    {"lock_name": lock_name},
                )
                logger.info(f"락 해제: {lock_name}")
