"""Defines the User model for the database."""

from sqlalchemy import Column, INTEGER, VARCHAR, BOOLEAN
from sqlalchemy.orm import relationship
from services.db.base import Base


class User(Base):
    """Database model representing a user."""

    __tablename__ = "User"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    username = Column(VARCHAR(255), nullable=False, unique=True)
    password = Column(VARCHAR(255), nullable=False)
    is_active = Column(BOOLEAN, nullable=False)

    connections = relationship(
        "Connection",
        secondary="User_Connection",
        back_populates="users",
        passive_deletes=True
    )

    portfolios = relationship(
        "Portfolio",
        back_populates="user",
        cascade="all, delete-orphan"
    )
