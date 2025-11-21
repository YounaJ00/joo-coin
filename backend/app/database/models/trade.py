"""
Trade 엔티티
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models.enums import RiskLevel, TradeType


class Trade(Base):
    """거래 내역"""

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    coin_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("coins.id"), nullable=False
    )
    trade_type: Mapped[str] = mapped_column(String(10), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(10), nullable=False)
    ai_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # 관계 설정
    coin = relationship("Coin", back_populates="trades")

    @property
    def trade_type_enum(self) -> TradeType:
        """trade_type을 Enum으로 반환"""
        return TradeType(self.trade_type)

    @property
    def risk_level_enum(self) -> RiskLevel:
        """risk_level을 Enum으로 반환"""
        return RiskLevel(self.risk_level)
