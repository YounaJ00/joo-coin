import traceback
from logging import Logger

from app.common.model.base import get_session_maker
from app.common.named_lock import named_lock
from app.trade.service.trade_service import TradeService

logger = Logger(__name__)


async def trade_execution_job() -> None:
    """
    주기적으로 실행되는 자동 거래 작업

    모든 활성화된 코인에 대해 AI 분석을 수행하고 거래를 실행합니다.
    MySQL Named Lock을 사용하여 여러 워커에서 동시 실행을 방지합니다.
    """

    # Named Lock 획득 시도 (즉시 반환, 대기 없음)
    async with named_lock("trade_execution", timeout=0) as acquired:
        if not acquired:
            logger.info("🤩 다른 워커가 거래 작업을 실행 중입니다. 스킵합니다.")
            return

        session_maker = get_session_maker()

        try:
            async with session_maker() as session:
                trade_service = TradeService(session=session)
                logger.info("🚀 자동 거래 작업 시작")
                await trade_service.execute()

        except Exception as e:
            logger.error(f"거래 실행 중 오류 발생: {str(e)}\n{traceback.format_exc()}")
