"""
기본 Repository 클래스
"""

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    기본 CRUD 연산을 제공하는 Repository

    Args:
        model: SQLAlchemy 모델 클래스
        session: 데이터베이스 세션
    """

    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, entity: T) -> T:
        """엔티티 생성"""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, id: int) -> Optional[T]:
        """ID로 엔티티 조회"""
        return await self.session.get(self.model, id)

    async def get_all(self) -> List[T]:
        """모든 엔티티 조회"""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def update(self, entity: T) -> T:
        """엔티티 업데이트"""
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        """엔티티 삭제"""
        await self.session.delete(entity)
        await self.session.commit()
