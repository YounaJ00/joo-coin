"""
Coin 엔티티
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.model.base import Base


class Coin(Base):
    """거래 가능한 코인 목록"""

    __tablename__ = "coins"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # 관계 설정
    trades = relationship("Trade", back_populates="coin")
