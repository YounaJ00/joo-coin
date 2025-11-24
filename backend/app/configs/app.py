from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.api.v1.v1_router import v1_router
from app.common.model.base import get_engine
from app.configs.config import settings
from app.configs.scheduling_tasks import trade_execution_job

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    애플리케이션 수명 주기 관리

    시작 시 데이터베이스 연결을 확인하고, 종료 시 연결을 정리합니다.
    """
    # 시작: 데이터베이스 연결 확인
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)  # 연결 테스트

    # 스케줄러 시작
    # scheduler.add_job(trade_execution_job, "interval", seconds=30)
    # scheduler.start()

    yield

    # 종료: 스케줄러 및 엔진 정리
    scheduler.shutdown()
    await engine.dispose()


def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션 인스턴스 생성

    Returns:
        FastAPI: 설정이 완료된 FastAPI 인스턴스
    """
    # FastAPI 애플리케이션 생성
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/swagger-ui/index.html",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API 라우터 등록
    app.include_router(
        v1_router,
    )

    return app
