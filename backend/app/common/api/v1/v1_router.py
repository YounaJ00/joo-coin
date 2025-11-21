"""
API v1 라우터

모든 v1 API 엔드포인트를 여기에 등록합니다.
"""

from fastapi import APIRouter

from app.coin.controller.my_coin_controller import coin_router
from app.trade.controller.trade_controller import trade_router
from app.upbit.controller.upbit_controller import upbit_router

# API 라우터 생성
v1_router = APIRouter(prefix="/api/v1")

# 도메인별 라우터 등록
v1_router.include_router(coin_router)
v1_router.include_router(upbit_router)
v1_router.include_router(trade_router)
