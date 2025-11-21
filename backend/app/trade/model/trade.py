"""
Trade 엔티티
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.model.base import Base
from app.trade.model.enums import RiskLevel, TradeStatus, TradeType


class Trade(Base):
    """거래 내역"""

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    coin_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("coins.id"), nullable=True
    )
    trade_type: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    price: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, default=Decimal("0")
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, default=Decimal("0")
    )
    risk_level: Mapped[str] = mapped_column(
        String(10), nullable=False, default=RiskLevel.NONE.value
    )
    status: Mapped[TradeStatus] = mapped_column(String(20), nullable=False)
    ai_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # 관계 설정
    coin = relationship("Coin", back_populates="trades")

    @property
    def trade_type_enum(self) -> Optional[TradeType]:
        """trade_type을 Enum으로 반환"""
        return TradeType(self.trade_type) if self.trade_type else None

    @property
    def risk_level_enum(self) -> RiskLevel:
        """risk_level을 Enum으로 반환"""
        return RiskLevel(self.risk_level)
