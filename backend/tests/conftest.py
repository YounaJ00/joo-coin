"""
pytest 전역 설정 및 공통 fixture
"""
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.client.open_ai_client import OpenAIClient
from app.ai.dto.ai_analysis_response import AiAnalysisResponse, Decision, RiskLevel
from app.ballance.repository.balance_repository import BalanceRepository
from app.coin.model.coin import Coin
from app.coin.service.coin_service import CoinService
from app.trade.model.enums import TradeStatus, TradeType
from app.trade.model.trade import Trade
from app.trade.repository.trade_repository import TradeRepository
from app.trade.service.trade_service import TradeService
from app.upbit.client.upbit_client import UpbitClient


@pytest.fixture
def mock_session():
    """AsyncSession Mock"""
    session = MagicMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_trade_repository(mocker):
    """TradeRepository Mock"""
    repo = mocker.MagicMock(spec=TradeRepository)
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.get_all_with_coin_paginated = AsyncMock()
    return repo


@pytest.fixture
def mock_balance_repository(mocker):
    """BalanceRepository Mock"""
    repo = mocker.MagicMock(spec=BalanceRepository)
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def mock_coin_service(mocker):
    """CoinService Mock"""
    service = mocker.MagicMock(spec=CoinService)
    service.get_all_active = AsyncMock()
    return service


@pytest.fixture
def mock_upbit_client(mocker):
    """UpbitClient Mock"""
    client = mocker.MagicMock(spec=UpbitClient)
    client.get_krw_balance = MagicMock()
    client.get_coin_balance = MagicMock()
    client.get_current_price = MagicMock()
    client.get_ohlcv_raw = MagicMock()
    client.buy = MagicMock()
    client.sell = MagicMock()
    return client


@pytest.fixture
def mock_ai_client(mocker):
    """OpenAIClient Mock"""
    client = mocker.MagicMock(spec=OpenAIClient)
    client.get_bitcoin_trading_decision = MagicMock()
    return client


@pytest.fixture
def trade_service(
    mock_session,
    mock_trade_repository,
    mock_balance_repository,
    mock_coin_service,
    mock_upbit_client,
    mock_ai_client,
    mocker,
):
    """TradeService 인스턴스 생성 (Mock 주입)"""
    # TradeService __init__에서 생성되는 객체들을 Mock으로 대체
    mocker.patch(
        "app.trade.service.trade_service.TradeRepository",
        return_value=mock_trade_repository,
    )
    mocker.patch(
        "app.trade.service.trade_service.BalanceRepository",
        return_value=mock_balance_repository,
    )
    mocker.patch(
        "app.trade.service.trade_service.CoinService",
        return_value=mock_coin_service,
    )
    mocker.patch(
        "app.trade.service.trade_service.UpbitClient",
        return_value=mock_upbit_client,
    )
    mocker.patch(
        "app.trade.service.trade_service.OpenAIClient",
        return_value=mock_ai_client,
    )

    service = TradeService(mock_session)

    return service


@pytest.fixture
def sample_coin():
    """테스트용 코인 데이터"""
    coin = MagicMock(spec=Coin)
    coin.id = 1
    coin.name = "KRW-BTC"
    coin.is_deleted = False
    return coin


@pytest.fixture
def sample_ai_result_buy():
    """매수 결정 AI 응답"""
    return AiAnalysisResponse(
        decision=Decision.BUY,
        confidence=0.85,
        reason="상승 추세 예상",
        risk_level=RiskLevel.MEDIUM,
        timestamp=datetime.utcnow(),
    )


@pytest.fixture
def sample_ai_result_sell():
    """매도 결정 AI 응답"""
    return AiAnalysisResponse(
        decision=Decision.SELL,
        confidence=0.75,
        reason="하락 추세 예상",
        risk_level=RiskLevel.HIGH,
        timestamp=datetime.utcnow(),
    )


@pytest.fixture
def sample_ai_result_hold():
    """보유 결정 AI 응답"""
    return AiAnalysisResponse(
        decision=Decision.HOLD,
        confidence=0.60,
        reason="관망 필요",
        risk_level=RiskLevel.LOW,
        timestamp=datetime.utcnow(),
    )


@pytest.fixture
def sample_trade():
    """테스트용 거래 데이터"""
    return Trade(
        id=1,
        coin_id=1,
        trade_type=TradeType.BUY.value,
        price=Decimal("50000000"),
        amount=Decimal("0.001"),
        risk_level=RiskLevel.MEDIUM.value,
        status=TradeStatus.SUCCESS,
        ai_reason="상승 추세 예상",
        execution_reason="매수 완료",
    )
