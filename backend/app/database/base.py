"""
SQLAlchemy 데이터베이스 설정

engine, session, Base 클래스를 제공합니다.
"""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.configs.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 모델 기본 클래스"""

    pass


def get_async_database_url() -> str:
    """DB URL을 비동기 URL로 변환"""
    url = settings.DATABASE_URL
    # 이미 비동기 드라이버인 경우 그대로 반환
    if "aiomysql" in url or "asyncmy" in url:
        return url
    # 동기 드라이버를 비동기로 변환
    if url.startswith("mysql+pymysql"):
        return url.replace("mysql+pymysql", "mysql+aiomysql")
    if url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+aiomysql://")
    return url


@lru_cache
def get_engine():
    """비동기 엔진을 lazy하게 생성"""
    return create_async_engine(
        get_async_database_url(),
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        echo=False,
    )


@lru_cache
def get_session_maker():
    """세션 팩토리를 lazy하게 생성"""
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


# 하위 호환성을 위한 프로퍼티
@property
def engine():
    return get_engine()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    데이터베이스 세션을 생성하는 의존성 함수

    Yields:
        AsyncSession: 데이터베이스 세션
    """
    async with get_session_maker()() as session:
        yield session
