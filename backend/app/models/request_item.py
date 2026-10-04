"""RequestItem ORM Model

Represents individual purchase items extracted from messages or created/edited by members.
"""

from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class ItemStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PURCHASED = "PURCHASED"
    REJECTED = "REJECTED"


class RequestItem(Base):
    __tablename__ = "request_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    variant = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit = Column(String(50), nullable=False, default="piece")
    unit_price = Column(Numeric(10, 2), nullable=True, default=None)
    status = Column(Enum(ItemStatus), nullable=False, default=ItemStatus.PENDING, index=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="request_items")
    message = relationship("Message", back_populates="request_items")

    __table_args__ = (
        Index("ix_request_items_grouping", "name", "variant", "unit"),
    )
