import traceback
from decimal import Decimal
from logging import Logger
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.client.open_ai_client import OpenAIClient
from app.ai.dto.ai_analysis_response import AiAnalysisResponse, Decision, RiskLevel
from app.ballance.model.balance import Balance
from app.ballance.repository.balance_repository import BalanceRepository
from app.coin.model.coin import Coin
from app.coin.service.coin_service import CoinService
from app.trade.dto.transaction_response import (
    TransactionItemResponse,
    TransactionsResponse,
)
from app.trade.model.enums import TradeStatus, TradeType
from app.trade.model.trade import Trade
from app.trade.repository.trade_repository import TradeRepository
from app.upbit.client.upbit_client import UpbitClient

logger = Logger(__name__)


class TradeService:
    """거래 비즈니스 로직"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.trade_repository = TradeRepository(session)
        self.balance_repository = BalanceRepository(session)
        self.coin_service = CoinService(session=session)
        self.upbit_client = UpbitClient()
        self.ai_client = OpenAIClient()

    async def execute(
        self, fee_multiplier: float = 0.9995, min_order_amount: float = 5000.0
    ) -> List[Trade]:
        """
        모든 활성화된 코인에 대해 AI 분석 후 자동 거래를 실행합니다.

        @param fee_multiplier: 수수료를 고려한 실제 매매 가능 금액 계수 (기본: 0.9995)
        @param min_order_amount: 최소 주문 금액 (기본: 5000 KRW)
        @return: 실행된 거래 목록
        """
        executed_trades: List[Trade] = []

        # 1. 활성화된 모든 코인 조회
        active_coins = await self.coin_service.get_all_active()

        if not active_coins:
            reason = "거래 가능한 활성화된 코인이 없습니다."

            # NO_ACTION 상태로 기록
            trade = Trade(
                coin_id=None,
                trade_type=None,
                price=Decimal("0"),
                amount=Decimal("0"),
                risk_level=RiskLevel.NONE.value,
                status=TradeStatus.NO_ACTION,
                ai_reason=None,
                execution_reason=reason,
            )
            no_action_trade = await self.trade_repository.create(trade)
            executed_trades.append(no_action_trade)
            return executed_trades

        # 2. 현재 KRW 잔고 조회
        krw_balance = self.upbit_client.get_krw_balance()

        if krw_balance == 0:
            reason = f"KRW 잔고가 없습니다. 매수 불가 (잔고: {krw_balance:,.0f}원)"

            # NO_ACTION 상태로 기록
            trade = Trade(
                coin_id=None,
                trade_type=None,
                price=Decimal("0"),
                amount=Decimal("0"),
                risk_level=RiskLevel.NONE.value,
                status=TradeStatus.NO_ACTION,
                ai_reason=None,
                execution_reason=reason,
            )
            no_action_trade = await self.trade_repository.create(trade)
            executed_trades.append(no_action_trade)
            return executed_trades

        # 3. 각 코인에 대해 AI 분석 및 거래 실행
        for coin in active_coins:
            try:
                coin_trade: Optional[Trade] = await self._process_coin_trade(
                    coin=coin,
                    krw_balance=krw_balance,
                    fee_multiplier=fee_multiplier,
                    min_order_amount=min_order_amount,
                )

                if coin_trade:
                    executed_trades.append(coin_trade)
                    # 거래 후 KRW 잔고 갱신 (매수 시)
                    if (
                        coin_trade.trade_type == TradeType.BUY.value
                        and coin_trade.status == TradeStatus.SUCCESS
                    ):
                        krw_balance = self.upbit_client.get_krw_balance()

            except Exception as e:
                logger.error(
                    f"코인 {coin.name} 거래 처리 중 오류 발생: {str(e)}\ntraceback: {traceback.format_exc()}"
                )
                continue

        # 4. 거래 후 최종 잔고 기록
        await self._record_balance()

        return executed_trades

    async def _process_coin_trade(
        self,
        coin: Coin,
        krw_balance: float,
        fee_multiplier: float,
        min_order_amount: float,
    ) -> Optional[Trade]:
        """
        개별 코인에 대한 AI 분석 및 거래 처리

        @param coin: 거래 대상 코인
        @param krw_balance: 현재 KRW 잔고
        @param fee_multiplier: 수수료 계수
        @param min_order_amount: 최소 주문 금액
        @return: 실행된 거래 또는 None
        """
        coin_name = coin.name

        try:
            # 1. OHLCV 데이터 조회
            df = self.upbit_client.get_ohlcv_raw(coin_name)

            # 2. AI 분석
            ai_result: AiAnalysisResponse = self.ai_client.get_bitcoin_trading_decision(
                df
            )

        except Exception as e:
            # AI 분석 실패 시 FAILED 상태로 기록
            error_type = type(e).__name__
            error_message = str(e)

            # OpenAI RateLimitError 등 특정 에러 처리
            if "RateLimitError" in error_type or "429" in error_message:
                reason = f"AI 분석 실패 (OpenAI API quota 초과)\n에러: {error_message}"
            elif "APIError" in error_type or "OpenAI" in error_type:
                reason = f"AI 분석 실패 (OpenAI API 오류)\n에러 타입: {error_type}\n에러 메시지: {error_message}"
            else:
                reason = f"AI 분석 실패\n에러 타입: {error_type}\n에러 메시지: {error_message}"

            trade = Trade(
                coin_id=coin.id,
                trade_type=None,
                price=Decimal("0"),
                amount=Decimal("0"),
                risk_level=RiskLevel.NONE.value,
                status=TradeStatus.FAILED,
                ai_reason=None,
                execution_reason=reason,
            )
            return await self.trade_repository.create(trade)

        # 3. 현재 코인 잔고 조회
        coin_balance = self.upbit_client.get_coin_balance(coin_name)

        # 4. 결정에 따라 거래 실행
        if ai_result.decision == Decision.BUY:
            return await self._execute_buy(
                coin=coin,
                coin_name=coin_name,
                krw_balance=krw_balance,
                fee_multiplier=fee_multiplier,
                min_order_amount=min_order_amount,
                ai_result=ai_result,
            )

        elif ai_result.decision == Decision.SELL:
            return await self._execute_sell(
                coin=coin,
                coin_name=coin_name,
                coin_balance=coin_balance,
                fee_multiplier=fee_multiplier,
                min_order_amount=min_order_amount,
                ai_result=ai_result,
            )

        elif ai_result.decision == Decision.HOLD:
            # HOLD 결정도 기록으로 남김
            current_price = self.upbit_client.get_current_price(coin_name)

            trade = Trade(
                coin_id=coin.id,
                trade_type=TradeType.HOLD.value,
                price=Decimal(str(current_price)),
                amount=Decimal("0"),
                risk_level=ai_result.risk_level.value,
                status=TradeStatus.NO_ACTION,
                ai_reason=ai_result.reason,
                execution_reason=f"AI HOLD 결정 (Confidence: {ai_result.confidence:.2%})",
            )
            return await self.trade_repository.create(trade)

        return None

    async def _execute_buy(
        self,
        coin: Coin,
        coin_name: str,
        krw_balance: float,
        fee_multiplier: float,
        min_order_amount: float,
        ai_result: AiAnalysisResponse,
    ) -> Optional[Trade]:
        """매수 실행"""
        reasons = []
        reasons.append(
            f"AI 매수 결정: Confidence {ai_result.confidence:.2%}, Reason: {ai_result.reason}"
        )
        reasons.append(f"보유 KRW 잔고: {krw_balance:,.0f}원")

        available_buy_amount = krw_balance * fee_multiplier

        if available_buy_amount < min_order_amount:
            reason = f"KRW 잔고가 {min_order_amount}원 미만입니다. 매수 불가 (가용 금액: {available_buy_amount:,.0f}원)"
            reasons.append(reason)

            # 실패한 거래도 기록
            trade = Trade(
                coin_id=coin.id,
                trade_type=TradeType.BUY.value,
                price=Decimal("0"),
                amount=Decimal("0"),
                risk_level=ai_result.risk_level.value,
                status=TradeStatus.FAILED,
                ai_reason=ai_result.reason,
                execution_reason="\n".join(reasons),
            )
            return await self.trade_repository.create(trade)

        # 매수 전 현재 가격 조회
        current_price = self.upbit_client.get_current_price(coin_name)
        reasons.append(f"현재 {coin_name} 가격: {current_price:,.0f}원")

        # 매수한 코인 수량 계산 (수수료 고려)
        coin_amount = (available_buy_amount / current_price) * fee_multiplier
        reasons.append(f"매수 예정 수량: {coin_amount:.8f} {coin_name}")

        # PENDING 상태로 거래 기록 생성
        trade = Trade(
            coin_id=coin.id,
            trade_type=TradeType.BUY.value,
            price=Decimal(str(current_price)),
            amount=Decimal(str(coin_amount)),
            risk_level=ai_result.risk_level.value,
            status=TradeStatus.PENDING,
            ai_reason=ai_result.reason,
            execution_reason="\n".join(reasons),
        )
        trade = await self.trade_repository.create(trade)

        try:
            # 매수 실행
            self.upbit_client.buy(coin_name, available_buy_amount)

            reasons.append(f"매수 주문 실행 완료: {available_buy_amount:,.0f}원")
            trade.status = TradeStatus.SUCCESS
            trade.execution_reason = "\n".join(reasons)

        except Exception as e:
            reasons.append(f"매수 주문 실패: {str(e)}")
            trade.status = TradeStatus.FAILED
            trade.execution_reason = "\n".join(reasons)

        return await self.trade_repository.update(trade)

    async def _execute_sell(
        self,
        coin: Coin,
        coin_name: str,
        coin_balance: float,
        fee_multiplier: float,
        min_order_amount: float,
        ai_result: AiAnalysisResponse,
    ) -> Optional[Trade]:
        """매도 실행"""
        reasons = []
        reasons.append(
            f"AI 매도 결정: Confidence {ai_result.confidence:.2%}, Reason: {ai_result.reason}"
        )
        reasons.append(f"보유 {coin_name} 수량: {coin_balance:.8f}")

        if coin_balance == 0:
            reason = "보유 코인이 없습니다. 매도 불가"
            reasons.append(reason)

            # 실패한 거래도 기록
            trade = Trade(
                coin_id=coin.id,
                trade_type=TradeType.SELL.value,
                price=Decimal("0"),
                amount=Decimal("0"),
                risk_level=ai_result.risk_level.value,
                status=TradeStatus.FAILED,
                ai_reason=ai_result.reason,
                execution_reason="\n".join(reasons),
            )
            return await self.trade_repository.create(trade)

        # 현재 매도 호가 조회
        current_price = self.upbit_client.get_current_price(coin_name)
        reasons.append(f"현재 {coin_name} 가격: {current_price:,.0f}원")

        # 매도 시 수수료 제외 전 총 매도 금액
        gross_amount = coin_balance * current_price
        available_sell_amount = gross_amount * fee_multiplier
        reasons.append(
            f"매도 예상 금액: {available_sell_amount:,.0f}원 (수수료 차감 후)"
        )

        if available_sell_amount < min_order_amount:
            reason = f"매도 예상 금액이 {min_order_amount}원 미만입니다. 매도 불가"
            reasons.append(reason)

            # 실패한 거래도 기록
            trade = Trade(
                coin_id=coin.id,
                trade_type=TradeType.SELL.value,
                price=Decimal(str(current_price)),
                amount=Decimal(str(coin_balance)),
                risk_level=ai_result.risk_level.value,
                status=TradeStatus.FAILED,
                ai_reason=ai_result.reason,
                execution_reason="\n".join(reasons),
            )
            return await self.trade_repository.create(trade)

        # PENDING 상태로 거래 기록 생성
        trade = Trade(
            coin_id=coin.id,
            trade_type=TradeType.SELL.value,
            price=Decimal(str(current_price)),
            amount=Decimal(str(coin_balance)),
            risk_level=ai_result.risk_level.value,
            status=TradeStatus.PENDING,
            ai_reason=ai_result.reason,
            execution_reason="\n".join(reasons),
        )
        trade = await self.trade_repository.create(trade)

        try:
            # 매도 실행
            self.upbit_client.sell(coin_name, coin_balance)

            reasons.append(
                f"매도 주문 실행 완료: {coin_balance:.8f} {coin_name} (약 {available_sell_amount:,.0f}원)"
            )
            trade.status = TradeStatus.SUCCESS
            trade.execution_reason = "\n".join(reasons)

        except Exception as e:
            reasons.append(f"매도 주문 실패: {str(e)}")
            trade.status = TradeStatus.FAILED
            trade.execution_reason = "\n".join(reasons)

        return await self.trade_repository.update(trade)

    async def _record_balance(self) -> None:
        """현재 잔고를 데이터베이스에 기록"""
        krw_balance = self.upbit_client.get_krw_balance()

        # 모든 활성 코인의 총 보유량 조회 (KRW 가치로 환산)
        active_coins = await self.coin_service.get_all_active()
        total_coin_value = 0.0

        for coin in active_coins:
            coin_balance = self.upbit_client.get_coin_balance(coin.name)
            if coin_balance > 0:
                current_price = self.upbit_client.get_current_price(coin.name)
                total_coin_value += coin_balance * current_price

        # 잔고 기록
        balance = Balance(
            amount=Decimal(str(krw_balance)),
            coin_amount=Decimal(str(total_coin_value)),
        )

        await self.balance_repository.create(balance)

    async def get_transactions(
        self, cursor: Optional[int] = None, limit: int = 20
    ) -> TransactionsResponse:
        """
        거래 내역을 커서 기반 페이지네이션으로 조회

        @param cursor: 이전 페이지의 마지막 거래 ID (None이면 첫 페이지)
        @param limit: 페이지당 조회할 항목 수 (기본: 20)
        @return: 거래 내역 목록 응답 (다음 페이지 정보 포함)
        """
        # limit + 1개를 조회하여 다음 페이지 존재 여부 확인
        trades = await self.trade_repository.get_all_with_coin_paginated(
            cursor=cursor, limit=limit + 1
        )

        # 다음 페이지 존재 여부 판단
        has_next = len(trades) > limit

        # 실제 반환할 항목은 limit개만
        if has_next:
            trades = trades[:limit]
            next_cursor = trades[-1].id if trades else None
        else:
            next_cursor = None

        items = [
            TransactionItemResponse.from_trade(
                trade=trade, coin_name=trade.coin.name if trade.coin else None
            )
            for trade in trades
        ]

        return TransactionsResponse(
            items=items, next_cursor=next_cursor, has_next=has_next
        )
