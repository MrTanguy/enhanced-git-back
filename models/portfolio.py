from sqlalchemy import JSON, Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from services.db.base import Base
from ulid import ulid


class Portfolio(Base):
    __tablename__ = 'Portfolio'

    uuid = Column(String(26), primary_key=True, unique=True, nullable=False, default=lambda: ulid())
    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relation avec User (One-to-Many)
    user = relationship("User", back_populates="portfolios")
