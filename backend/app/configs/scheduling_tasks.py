import traceback
from logging import Logger

from app.common.model.base import get_session_maker
from app.trade.service.trade_service import TradeService

logger = Logger(__name__)


async def trade_execution_job() -> None:
    """
    주기적으로 실행되는 자동 거래 작업

    모든 활성화된 코인에 대해 AI 분석을 수행하고 거래를 실행합니다.
    """

    session_maker = get_session_maker()

    try:
        async with session_maker() as session:
            trade_service = TradeService(session=session)
            logger.info("🚀 자동 거래 작업 시작")
            await trade_service.execute()

    except Exception as e:
        logger.info(f"❌ 거래 실행 중 오류 발생: {str(e)}\n{traceback.format_exc()}")

        traceback.print_exc()
