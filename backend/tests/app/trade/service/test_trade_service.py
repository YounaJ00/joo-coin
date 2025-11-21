"""
TradeService 테스트
모든 메서드와 분기를 테스트합니다.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ai.dto.ai_analysis_response import AiAnalysisResponse, Decision, RiskLevel
from app.coin.model.coin import Coin
from app.trade.dto.transaction_response import (
    TransactionItemResponse,
    TransactionsResponse,
)
from app.trade.model.enums import TradeStatus, TradeType
from app.trade.model.trade import Trade


class TestExecute:
    """execute() 메서드 테스트"""

    async def test_execute_no_active_coins(
        self, trade_service, mock_coin_service, mock_trade_repository
    ):
        """활성 코인이 없는 경우 NO_ACTION 상태로 기록"""
        # Given: 활성 코인이 없음
        mock_coin_service.get_all_active.return_value = []

        mock_trade = Trade(
            coin_id=None,
            trade_type=None,
            price=Decimal("0"),
            amount=Decimal("0"),
            risk_level=RiskLevel.NONE.value,
            status=TradeStatus.NO_ACTION,
            ai_reason=None,
            execution_reason="거래 가능한 활성화된 코인이 없습니다.",
        )
        mock_trade_repository.create.return_value = mock_trade

        # When: execute 실행
        result = await trade_service.execute()

        # Then: NO_ACTION 거래 기록 생성
        assert len(result) == 1
        assert result[0].status == TradeStatus.NO_ACTION
        assert "활성화된 코인이 없습니다" in result[0].execution_reason
        mock_trade_repository.create.assert_called_once()

    async def test_execute_zero_krw_balance(
        self,
        trade_service,
        mock_coin_service,
        mock_upbit_client,
        mock_trade_repository,
        sample_coin,
    ):
        """KRW 잔고가 0인 경우 NO_ACTION 상태로 기록"""
        # Given: 활성 코인은 있지만 KRW 잔고가 0
        mock_coin_service.get_all_active.return_value = [sample_coin]
        mock_upbit_client.get_krw_balance.return_value = 0

        mock_trade = Trade(
            coin_id=None,
            trade_type=None,
            price=Decimal("0"),
            amount=Decimal("0"),
            risk_level=RiskLevel.NONE.value,
            status=TradeStatus.NO_ACTION,
            ai_reason=None,
            execution_reason="KRW 잔고가 없습니다. 매수 불가 (잔고: 0원)",
        )
        mock_trade_repository.create.return_value = mock_trade

        # When: execute 실행
        result = await trade_service.execute()

        # Then: NO_ACTION 거래 기록 생성
        assert len(result) == 1
        assert result[0].status == TradeStatus.NO_ACTION
        assert "KRW 잔고가 없습니다" in result[0].execution_reason
        mock_trade_repository.create.assert_called_once()

    async def test_execute_success_with_buy(
        self,
        trade_service,
        mock_coin_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        mock_balance_repository,
        sample_coin,
        sample_ai_result_buy,
    ):
        """매수 성공 케이스"""
        # Given: 활성 코인, KRW 잔고, AI 매수 결정
        mock_coin_service.get_all_active.return_value = [sample_coin]
        mock_upbit_client.get_krw_balance.return_value = 100000
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_upbit_client.get_coin_balance.return_value = 0
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.return_value = sample_ai_result_buy
        mock_upbit_client.buy.return_value = None

        pending_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.PENDING,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 예정",
        )

        success_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.SUCCESS,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 완료",
        )

        mock_trade_repository.create.return_value = pending_trade
        mock_trade_repository.update.return_value = success_trade

        # When: execute 실행
        result = await trade_service.execute()

        # Then: 매수 성공
        assert len(result) == 1
        assert result[0].status == TradeStatus.SUCCESS
        assert result[0].trade_type == TradeType.BUY.value
        mock_upbit_client.buy.assert_called_once()
        mock_balance_repository.create.assert_called_once()

    async def test_execute_success_with_sell(
        self,
        trade_service,
        mock_coin_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        mock_balance_repository,
        sample_coin,
        sample_ai_result_sell,
    ):
        """매도 성공 케이스"""
        # Given: 활성 코인, 코인 잔고, AI 매도 결정
        mock_coin_service.get_all_active.return_value = [sample_coin]
        mock_upbit_client.get_krw_balance.return_value = 100000
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_upbit_client.get_coin_balance.return_value = 0.001
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.return_value = sample_ai_result_sell
        mock_upbit_client.sell.return_value = None

        pending_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.HIGH.value,
            status=TradeStatus.PENDING,
            ai_reason=sample_ai_result_sell.reason,
            execution_reason="매도 예정",
        )

        success_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.HIGH.value,
            status=TradeStatus.SUCCESS,
            ai_reason=sample_ai_result_sell.reason,
            execution_reason="매도 완료",
        )

        mock_trade_repository.create.return_value = pending_trade
        mock_trade_repository.update.return_value = success_trade

        # When: execute 실행
        result = await trade_service.execute()

        # Then: 매도 성공
        assert len(result) == 1
        assert result[0].status == TradeStatus.SUCCESS
        assert result[0].trade_type == TradeType.SELL.value
        mock_upbit_client.sell.assert_called_once()
        mock_balance_repository.create.assert_called_once()

    async def test_execute_with_exception(
        self,
        trade_service,
        mock_coin_service,
        mock_upbit_client,
        mock_ai_client,
        mock_balance_repository,
        sample_coin,
    ):
        """코인 거래 중 예외 발생 시 계속 진행"""
        # Given: 코인 처리 중 예외 발생
        mock_coin_service.get_all_active.return_value = [sample_coin]
        mock_upbit_client.get_krw_balance.return_value = 100000
        mock_upbit_client.get_ohlcv_raw.side_effect = Exception("API 오류")
        mock_upbit_client.get_coin_balance.return_value = 0

        # When: execute 실행 (예외가 발생해도 계속 진행)
        result = await trade_service.execute()

        # Then: 예외 발생해도 잔고 기록은 수행
        mock_balance_repository.create.assert_called_once()


class TestProcessCoinTrade:
    """_process_coin_trade() 메서드 테스트"""

    async def test_process_coin_trade_ai_analysis_failed(
        self,
        trade_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        sample_coin,
    ):
        """AI 분석 실패 시 FAILED 상태로 기록"""
        # Given: AI 분석 중 예외 발생
        mock_upbit_client.get_ohlcv_raw.side_effect = Exception("API 오류")

        failed_trade = Trade(
            coin_id=sample_coin.id,
            trade_type=None,
            price=Decimal("0"),
            amount=Decimal("0"),
            risk_level=RiskLevel.NONE.value,
            status=TradeStatus.FAILED,
            ai_reason=None,
            execution_reason="AI 분석 실패\n에러 타입: Exception\n에러 메시지: API 오류",
        )
        mock_trade_repository.create.return_value = failed_trade

        # When: _process_coin_trade 실행
        result = await trade_service._process_coin_trade(
            coin=sample_coin,
            krw_balance=100000,
            fee_multiplier=0.9995,
            min_order_amount=5000,
        )

        # Then: FAILED 거래 기록 생성
        assert result.status == TradeStatus.FAILED
        assert "AI 분석 실패" in result.execution_reason
        mock_trade_repository.create.assert_called_once()

    async def test_process_coin_trade_ai_rate_limit_error(
        self,
        trade_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        sample_coin,
    ):
        """AI 분석 중 RateLimitError 발생 시 FAILED 상태로 기록"""
        # Given: OpenAI RateLimitError 발생
        error = Exception("RateLimitError: quota exceeded")
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.side_effect = error

        failed_trade = Trade(
            coin_id=sample_coin.id,
            trade_type=None,
            price=Decimal("0"),
            amount=Decimal("0"),
            risk_level=RiskLevel.NONE.value,
            status=TradeStatus.FAILED,
            ai_reason=None,
            execution_reason="AI 분석 실패 (OpenAI API quota 초과)",
        )
        mock_trade_repository.create.return_value = failed_trade

        # When: _process_coin_trade 실행
        result = await trade_service._process_coin_trade(
            coin=sample_coin,
            krw_balance=100000,
            fee_multiplier=0.9995,
            min_order_amount=5000,
        )

        # Then: FAILED 거래 기록 생성
        assert result.status == TradeStatus.FAILED
        assert "quota 초과" in result.execution_reason
        mock_trade_repository.create.assert_called_once()

    async def test_process_coin_trade_ai_api_error(
        self,
        trade_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        sample_coin,
    ):
        """AI 분석 중 APIError 발생 시 FAILED 상태로 기록"""

        # Given: OpenAI APIError 발생
        class APIError(Exception):
            pass

        error = APIError("API connection failed")
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.side_effect = error

        failed_trade = Trade(
            coin_id=sample_coin.id,
            trade_type=None,
            price=Decimal("0"),
            amount=Decimal("0"),
            risk_level=RiskLevel.NONE.value,
            status=TradeStatus.FAILED,
            ai_reason=None,
            execution_reason="AI 분석 실패 (OpenAI API 오류)",
        )
        mock_trade_repository.create.return_value = failed_trade

        # When: _process_coin_trade 실행
        result = await trade_service._process_coin_trade(
            coin=sample_coin,
            krw_balance=100000,
            fee_multiplier=0.9995,
            min_order_amount=5000,
        )

        # Then: FAILED 거래 기록 생성
        assert result.status == TradeStatus.FAILED
        assert "API 오류" in result.execution_reason
        mock_trade_repository.create.assert_called_once()

    async def test_process_coin_trade_buy_decision(
        self,
        trade_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_buy,
    ):
        """AI 매수 결정 시 _execute_buy 호출"""
        # Given: AI가 매수 결정
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.return_value = sample_ai_result_buy
        mock_upbit_client.get_coin_balance.return_value = 0
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_upbit_client.buy.return_value = None

        pending_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.PENDING,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 예정",
        )

        success_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.SUCCESS,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 완료",
        )

        mock_trade_repository.create.return_value = pending_trade
        mock_trade_repository.update.return_value = success_trade

        # When: _process_coin_trade 실행
        result = await trade_service._process_coin_trade(
            coin=sample_coin,
            krw_balance=100000,
            fee_multiplier=0.9995,
            min_order_amount=5000,
        )

        # Then: 매수 실행
        assert result.trade_type == TradeType.BUY.value
        mock_upbit_client.buy.assert_called_once()

    async def test_process_coin_trade_sell_decision(
        self,
        trade_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_sell,
    ):
        """AI 매도 결정 시 _execute_sell 호출"""
        # Given: AI가 매도 결정
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.return_value = sample_ai_result_sell
        mock_upbit_client.get_coin_balance.return_value = 0.001
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_upbit_client.sell.return_value = None

        pending_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.HIGH.value,
            status=TradeStatus.PENDING,
            ai_reason=sample_ai_result_sell.reason,
            execution_reason="매도 예정",
        )

        success_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.HIGH.value,
            status=TradeStatus.SUCCESS,
            ai_reason=sample_ai_result_sell.reason,
            execution_reason="매도 완료",
        )

        mock_trade_repository.create.return_value = pending_trade
        mock_trade_repository.update.return_value = success_trade

        # When: _process_coin_trade 실행
        result = await trade_service._process_coin_trade(
            coin=sample_coin,
            krw_balance=100000,
            fee_multiplier=0.9995,
            min_order_amount=5000,
        )

        # Then: 매도 실행
        assert result.trade_type == TradeType.SELL.value
        mock_upbit_client.sell.assert_called_once()

    async def test_process_coin_trade_hold_decision(
        self,
        trade_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_hold,
    ):
        """AI HOLD 결정 시 NO_ACTION으로 기록"""
        # Given: AI가 HOLD 결정
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.return_value = sample_ai_result_hold
        mock_upbit_client.get_coin_balance.return_value = 0
        mock_upbit_client.get_current_price.return_value = 50000000

        hold_trade = Trade(
            coin_id=sample_coin.id,
            trade_type=TradeType.HOLD.value,
            price=Decimal("50000000"),
            amount=Decimal("0"),
            risk_level=RiskLevel.LOW.value,
            status=TradeStatus.NO_ACTION,
            ai_reason=sample_ai_result_hold.reason,
            execution_reason=f"AI HOLD 결정 (Confidence: {sample_ai_result_hold.confidence:.2%})",
        )
        mock_trade_repository.create.return_value = hold_trade

        # When: _process_coin_trade 실행
        result = await trade_service._process_coin_trade(
            coin=sample_coin,
            krw_balance=100000,
            fee_multiplier=0.9995,
            min_order_amount=5000,
        )

        # Then: HOLD 기록
        assert result.status == TradeStatus.NO_ACTION
        assert result.trade_type == TradeType.HOLD.value
        assert "HOLD 결정" in result.execution_reason


class TestExecuteBuy:
    """_execute_buy() 메서드 테스트"""

    async def test_execute_buy_insufficient_balance(
        self,
        trade_service,
        mock_upbit_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_buy,
    ):
        """KRW 잔고가 최소 주문 금액 미만인 경우 FAILED"""
        # Given: 가용 금액이 최소 주문 금액 미만
        krw_balance = 4000
        mock_upbit_client.get_current_price.return_value = 50000000

        async def create_trade(trade):
            return trade

        mock_trade_repository.create.side_effect = create_trade

        # When: _execute_buy 실행
        result = await trade_service._execute_buy(
            coin=sample_coin,
            coin_name=sample_coin.name,
            krw_balance=krw_balance,
            fee_multiplier=0.9995,
            min_order_amount=5000,
            ai_result=sample_ai_result_buy,
        )

        # Then: FAILED 상태
        assert result.status == TradeStatus.FAILED
        assert "5000원 미만입니다" in result.execution_reason
        mock_upbit_client.buy.assert_not_called()

    async def test_execute_buy_success(
        self,
        trade_service,
        mock_upbit_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_buy,
    ):
        """매수 성공"""
        # Given: 충분한 잔고
        krw_balance = 100000
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_upbit_client.buy.return_value = None

        pending_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.PENDING,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 예정",
        )

        success_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.SUCCESS,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 완료",
        )

        mock_trade_repository.create.return_value = pending_trade
        mock_trade_repository.update.return_value = success_trade

        # When: _execute_buy 실행
        result = await trade_service._execute_buy(
            coin=sample_coin,
            coin_name=sample_coin.name,
            krw_balance=krw_balance,
            fee_multiplier=0.9995,
            min_order_amount=5000,
            ai_result=sample_ai_result_buy,
        )

        # Then: SUCCESS 상태
        assert result.status == TradeStatus.SUCCESS
        mock_upbit_client.buy.assert_called_once()

    async def test_execute_buy_exception(
        self,
        trade_service,
        mock_upbit_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_buy,
    ):
        """매수 중 예외 발생 시 FAILED"""
        # Given: 매수 실행 중 예외 발생
        krw_balance = 100000
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_upbit_client.buy.side_effect = Exception("주문 실패")

        pending_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.PENDING,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 예정",
        )

        failed_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.FAILED,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 주문 실패: 주문 실패",
        )

        mock_trade_repository.create.return_value = pending_trade
        mock_trade_repository.update.return_value = failed_trade

        # When: _execute_buy 실행
        result = await trade_service._execute_buy(
            coin=sample_coin,
            coin_name=sample_coin.name,
            krw_balance=krw_balance,
            fee_multiplier=0.9995,
            min_order_amount=5000,
            ai_result=sample_ai_result_buy,
        )

        # Then: FAILED 상태
        assert result.status == TradeStatus.FAILED
        assert "매수 주문 실패" in result.execution_reason


class TestExecuteSell:
    """_execute_sell() 메서드 테스트"""

    async def test_execute_sell_no_coin_balance(
        self,
        trade_service,
        mock_upbit_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_sell,
    ):
        """코인 잔고가 0인 경우 FAILED"""
        # Given: 코인 잔고 0
        coin_balance = 0
        mock_upbit_client.get_current_price.return_value = 50000000

        failed_trade = Trade(
            coin_id=sample_coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal("0"),
            amount=Decimal("0"),
            risk_level=RiskLevel.HIGH.value,
            status=TradeStatus.FAILED,
            ai_reason=sample_ai_result_sell.reason,
            execution_reason="보유 코인이 없습니다",
        )
        mock_trade_repository.create.return_value = failed_trade

        # When: _execute_sell 실행
        result = await trade_service._execute_sell(
            coin=sample_coin,
            coin_name=sample_coin.name,
            coin_balance=coin_balance,
            fee_multiplier=0.9995,
            min_order_amount=5000,
            ai_result=sample_ai_result_sell,
        )

        # Then: FAILED 상태
        assert result.status == TradeStatus.FAILED
        assert "보유 코인이 없습니다" in result.execution_reason
        mock_upbit_client.sell.assert_not_called()

    async def test_execute_sell_below_min_amount(
        self,
        trade_service,
        mock_upbit_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_sell,
    ):
        """매도 예상 금액이 최소 주문 금액 미만인 경우 FAILED"""
        # Given: 매도 예상 금액이 최소 주문 금액 미만
        coin_balance = 0.00001
        mock_upbit_client.get_current_price.return_value = 50000000

        async def create_trade(trade):
            return trade

        mock_trade_repository.create.side_effect = create_trade

        # When: _execute_sell 실행
        result = await trade_service._execute_sell(
            coin=sample_coin,
            coin_name=sample_coin.name,
            coin_balance=coin_balance,
            fee_multiplier=0.9995,
            min_order_amount=5000,
            ai_result=sample_ai_result_sell,
        )

        # Then: FAILED 상태
        assert result.status == TradeStatus.FAILED
        assert "5000원 미만입니다" in result.execution_reason
        mock_upbit_client.sell.assert_not_called()

    async def test_execute_sell_success(
        self,
        trade_service,
        mock_upbit_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_sell,
    ):
        """매도 성공"""
        # Given: 충분한 코인 잔고
        coin_balance = 0.001
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_upbit_client.sell.return_value = None

        pending_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.HIGH.value,
            status=TradeStatus.PENDING,
            ai_reason=sample_ai_result_sell.reason,
            execution_reason="매도 예정",
        )

        success_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.HIGH.value,
            status=TradeStatus.SUCCESS,
            ai_reason=sample_ai_result_sell.reason,
            execution_reason="매도 완료",
        )

        mock_trade_repository.create.return_value = pending_trade
        mock_trade_repository.update.return_value = success_trade

        # When: _execute_sell 실행
        result = await trade_service._execute_sell(
            coin=sample_coin,
            coin_name=sample_coin.name,
            coin_balance=coin_balance,
            fee_multiplier=0.9995,
            min_order_amount=5000,
            ai_result=sample_ai_result_sell,
        )

        # Then: SUCCESS 상태
        assert result.status == TradeStatus.SUCCESS
        mock_upbit_client.sell.assert_called_once()

    async def test_execute_sell_exception(
        self,
        trade_service,
        mock_upbit_client,
        mock_trade_repository,
        sample_coin,
        sample_ai_result_sell,
    ):
        """매도 중 예외 발생 시 FAILED"""
        # Given: 매도 실행 중 예외 발생
        coin_balance = 0.001
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_upbit_client.sell.side_effect = Exception("주문 실패")

        pending_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.HIGH.value,
            status=TradeStatus.PENDING,
            ai_reason=sample_ai_result_sell.reason,
            execution_reason="매도 예정",
        )

        failed_trade = Trade(
            id=1,
            coin_id=sample_coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.HIGH.value,
            status=TradeStatus.FAILED,
            ai_reason=sample_ai_result_sell.reason,
            execution_reason="매도 주문 실패: 주문 실패",
        )

        mock_trade_repository.create.return_value = pending_trade
        mock_trade_repository.update.return_value = failed_trade

        # When: _execute_sell 실행
        result = await trade_service._execute_sell(
            coin=sample_coin,
            coin_name=sample_coin.name,
            coin_balance=coin_balance,
            fee_multiplier=0.9995,
            min_order_amount=5000,
            ai_result=sample_ai_result_sell,
        )

        # Then: FAILED 상태
        assert result.status == TradeStatus.FAILED
        assert "매도 주문 실패" in result.execution_reason


class TestRecordBalance:
    """_record_balance() 메서드 테스트"""

    async def test_record_balance(
        self,
        trade_service,
        mock_upbit_client,
        mock_coin_service,
        mock_balance_repository,
        sample_coin,
    ):
        """잔고 기록 테스트"""
        # Given: KRW 잔고와 활성 코인
        mock_upbit_client.get_krw_balance.return_value = 100000
        mock_coin_service.get_all_active.return_value = [sample_coin]
        mock_upbit_client.get_coin_balance.return_value = 0.001
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_balance_repository.create.return_value = None

        # When: _record_balance 실행
        await trade_service._record_balance()

        # Then: 잔고 기록 생성
        mock_balance_repository.create.assert_called_once()

        # 호출된 Balance 객체 검증
        call_args = mock_balance_repository.create.call_args
        balance = call_args[0][0]
        assert balance.amount == Decimal("100000")
        assert balance.coin_amount == Decimal("50000")  # 0.001 * 50000000


class TestGetTransactions:
    """get_transactions() 메서드 테스트"""

    async def test_get_transactions_first_page(
        self, trade_service, mock_trade_repository, sample_coin
    ):
        """첫 페이지 조회"""
        # Given: 15개의 거래 내역 (limit=20이므로 다음 페이지 없음)
        trades = []
        for i in range(15):
            trade = MagicMock()
            trade.id = i + 1
            trade.coin_id = sample_coin.id
            trade.trade_type = TradeType.BUY.value
            trade.price = Decimal("50000000")
            trade.amount = Decimal("0.001")
            trade.risk_level = RiskLevel.MEDIUM.value
            trade.status = TradeStatus.SUCCESS
            trade.ai_reason = "매수"
            trade.execution_reason = "완료"
            trade.created_at = datetime.utcnow()
            trade.coin = sample_coin
            trades.append(trade)

        mock_trade_repository.get_all_with_coin_paginated.return_value = trades

        # When: 첫 페이지 조회
        result = await trade_service.get_transactions(cursor=None, limit=20)

        # Then: 15개 반환, 다음 페이지 없음
        assert len(result.items) == 15
        assert result.has_next is False
        assert result.next_cursor is None

    async def test_get_transactions_with_cursor(
        self, trade_service, mock_trade_repository, sample_coin
    ):
        """커서로 다음 페이지 조회"""
        # Given: 21개의 거래 내역 (limit=20이므로 다음 페이지 있음)
        trades = []
        for i in range(21):
            trade = MagicMock()
            trade.id = i + 21
            trade.coin_id = sample_coin.id
            trade.trade_type = TradeType.BUY.value
            trade.price = Decimal("50000000")
            trade.amount = Decimal("0.001")
            trade.risk_level = RiskLevel.MEDIUM.value
            trade.status = TradeStatus.SUCCESS
            trade.ai_reason = "매수"
            trade.execution_reason = "완료"
            trade.created_at = datetime.utcnow()
            trade.coin = sample_coin
            trades.append(trade)

        mock_trade_repository.get_all_with_coin_paginated.return_value = trades

        # When: 커서로 다음 페이지 조회
        result = await trade_service.get_transactions(cursor=20, limit=20)

        # Then: 20개만 반환, 다음 페이지 있음
        assert len(result.items) == 20
        assert result.has_next is True
        assert result.next_cursor == 40  # 마지막 항목의 ID

    async def test_get_transactions_last_page(
        self, trade_service, mock_trade_repository, sample_coin
    ):
        """마지막 페이지 조회"""
        # Given: 5개의 거래 내역 (limit=20이므로 다음 페이지 없음)
        trades = []
        for i in range(5):
            trade = MagicMock()
            trade.id = i + 41
            trade.coin_id = sample_coin.id
            trade.trade_type = TradeType.BUY.value
            trade.price = Decimal("50000000")
            trade.amount = Decimal("0.001")
            trade.risk_level = RiskLevel.MEDIUM.value
            trade.status = TradeStatus.SUCCESS
            trade.ai_reason = "매수"
            trade.execution_reason = "완료"
            trade.created_at = datetime.utcnow()
            trade.coin = sample_coin
            trades.append(trade)

        mock_trade_repository.get_all_with_coin_paginated.return_value = trades

        # When: 마지막 페이지 조회
        result = await trade_service.get_transactions(cursor=40, limit=20)

        # Then: 5개만 반환, 다음 페이지 없음
        assert len(result.items) == 5
        assert result.has_next is False
        assert result.next_cursor is None

    async def test_get_transactions_empty(self, trade_service, mock_trade_repository):
        """빈 거래 내역 조회"""
        # Given: 거래 내역 없음
        mock_trade_repository.get_all_with_coin_paginated.return_value = []

        # When: 조회
        result = await trade_service.get_transactions(cursor=None, limit=20)

        # Then: 빈 목록 반환
        assert len(result.items) == 0
        assert result.has_next is False
        assert result.next_cursor is None

    async def test_get_transactions_with_null_coin(
        self, trade_service, mock_trade_repository
    ):
        """코인이 없는 거래 내역 조회"""
        # Given: 코인이 없는 거래 (coin_id=None)
        trade = MagicMock()
        trade.id = 1
        trade.coin_id = None
        trade.trade_type = None
        trade.price = Decimal("0")
        trade.amount = Decimal("0")
        trade.risk_level = RiskLevel.NONE.value
        trade.status = TradeStatus.NO_ACTION
        trade.ai_reason = None
        trade.execution_reason = "활성화된 코인이 없습니다"
        trade.created_at = datetime.utcnow()
        trade.coin = None
        mock_trade_repository.get_all_with_coin_paginated.return_value = [trade]

        # When: 조회
        result = await trade_service.get_transactions(cursor=None, limit=20)

        # Then: 코인 이름이 None인 항목 반환
        assert len(result.items) == 1
        assert result.items[0].coin_name is None
        assert result.items[0].coin_id is None


class TestExecuteMultipleCoins:
    """여러 코인에 대한 execute() 테스트"""

    async def test_execute_multiple_coins_with_balance_refresh(
        self,
        trade_service,
        mock_coin_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        mock_balance_repository,
        sample_ai_result_buy,
    ):
        """여러 코인 매수 시 잔고 갱신 확인"""
        # Given: 2개의 활성 코인
        coin1 = MagicMock()
        coin1.id = 1
        coin1.name = "KRW-BTC"

        coin2 = MagicMock()
        coin2.id = 2
        coin2.name = "KRW-ETH"

        mock_coin_service.get_all_active.return_value = [coin1, coin2]
        # 초기, 첫 매수 후, record_balance에서 2번 호출
        mock_upbit_client.get_krw_balance.side_effect = [100000, 50000, 25000, 25000]
        mock_upbit_client.get_current_price.return_value = 50000000
        mock_upbit_client.get_coin_balance.return_value = 0
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.return_value = sample_ai_result_buy
        mock_upbit_client.buy.return_value = None

        pending_trade = Trade(
            id=1,
            coin_id=1,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.PENDING,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 예정",
        )

        success_trade = Trade(
            id=1,
            coin_id=1,
            trade_type=TradeType.BUY.value,
            price=Decimal("50000000"),
            amount=Decimal("0.001"),
            risk_level=RiskLevel.MEDIUM.value,
            status=TradeStatus.SUCCESS,
            ai_reason=sample_ai_result_buy.reason,
            execution_reason="매수 완료",
        )

        mock_trade_repository.create.return_value = pending_trade
        mock_trade_repository.update.return_value = success_trade

        # When: execute 실행
        result = await trade_service.execute()

        # Then: 2개의 거래 실행, 잔고 갱신 호출됨
        assert len(result) == 2
        # 첫 번째 매수 후 잔고 갱신이 호출되어야 함
        assert mock_upbit_client.get_krw_balance.call_count >= 2


class TestRecordBalanceEdgeCases:
    """_record_balance() 엣지 케이스 테스트"""

    async def test_record_balance_no_coin_balance(
        self,
        trade_service,
        mock_upbit_client,
        mock_coin_service,
        mock_balance_repository,
        sample_coin,
    ):
        """코인 잔고가 0인 경우"""
        # Given: 코인 잔고 0
        mock_upbit_client.get_krw_balance.return_value = 100000
        mock_coin_service.get_all_active.return_value = [sample_coin]
        mock_upbit_client.get_coin_balance.return_value = 0
        mock_balance_repository.create.return_value = None

        # When: _record_balance 실행
        await trade_service._record_balance()

        # Then: 잔고 기록 생성 (coin_amount=0)
        mock_balance_repository.create.assert_called_once()
        call_args = mock_balance_repository.create.call_args
        balance = call_args[0][0]
        assert balance.coin_amount == Decimal("0")

    async def test_record_balance_no_active_coins(
        self,
        trade_service,
        mock_upbit_client,
        mock_coin_service,
        mock_balance_repository,
    ):
        """활성 코인이 없는 경우"""
        # Given: 활성 코인 없음
        mock_upbit_client.get_krw_balance.return_value = 100000
        mock_coin_service.get_all_active.return_value = []
        mock_balance_repository.create.return_value = None

        # When: _record_balance 실행
        await trade_service._record_balance()

        # Then: 잔고 기록 생성 (coin_amount=0)
        mock_balance_repository.create.assert_called_once()
        call_args = mock_balance_repository.create.call_args
        balance = call_args[0][0]
        assert balance.coin_amount == Decimal("0")


class TestProcessCoinTradeEdgeCases:
    """_process_coin_trade() 엣지 케이스 테스트"""

    async def test_process_coin_trade_openai_error_type(
        self,
        trade_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        sample_coin,
    ):
        """AI 분석 중 OpenAI 에러 타입 발생"""

        # Given: OpenAI 타입 에러 발생
        class OpenAIError(Exception):
            pass

        error = OpenAIError("Connection error")
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.side_effect = error

        async def create_trade(trade):
            return trade

        mock_trade_repository.create.side_effect = create_trade

        # When: _process_coin_trade 실행
        result = await trade_service._process_coin_trade(
            coin=sample_coin,
            krw_balance=100000,
            fee_multiplier=0.9995,
            min_order_amount=5000,
        )

        # Then: FAILED 거래 기록 생성
        assert result.status == TradeStatus.FAILED
        assert "OpenAI" in result.execution_reason

    async def test_process_coin_trade_429_error(
        self,
        trade_service,
        mock_upbit_client,
        mock_ai_client,
        mock_trade_repository,
        sample_coin,
    ):
        """AI 분석 중 429 에러 메시지 발생"""
        # Given: 429 에러 메시지 발생
        error = Exception("Error 429: Rate limit exceeded")
        mock_upbit_client.get_ohlcv_raw.return_value = MagicMock()
        mock_ai_client.get_bitcoin_trading_decision.side_effect = error

        async def create_trade(trade):
            return trade

        mock_trade_repository.create.side_effect = create_trade

        # When: _process_coin_trade 실행
        result = await trade_service._process_coin_trade(
            coin=sample_coin,
            krw_balance=100000,
            fee_multiplier=0.9995,
            min_order_amount=5000,
        )

        # Then: FAILED 거래 기록 생성 (quota 초과)
        assert result.status == TradeStatus.FAILED
        assert "quota 초과" in result.execution_reason
