"""Defines the Connection model for external service integrations."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from services.db.base import Base


class Connection(Base):
    """Database model representing an external account connection."""

    __tablename__ = "Connection"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, nullable=False)
    website = Column(String(20), nullable=False)
    access_token = Column(String(50), nullable=False)

    users = relationship(
        "User",
        secondary="User_Connection",
        back_populates="connections",
        passive_deletes=True
    )
