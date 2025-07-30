"""Defines the Portfolio model representing user portfolios."""

from sqlalchemy import JSON, Column, Integer, String, ForeignKey, TIMESTAMP, func
from ulid import ulid
from sqlalchemy.orm import relationship
from services.db.base import Base


class Portfolio(Base):
    """Database model for user portfolios."""

    __tablename__ = 'Portfolio'

    uuid = Column(String(26), primary_key=True, unique=True, nullable=False, default=ulid)
    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="portfolios")
