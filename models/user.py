from sqlalchemy import Column, INTEGER, VARCHAR, BOOLEAN
from sqlalchemy.orm import relationship
from services.db.base import Base


class User(Base):
    __tablename__ = 'User'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    username = Column(VARCHAR(255), nullable=False, unique=True)
    password = Column(VARCHAR(255), nullable=False)
    is_active = Column(BOOLEAN, nullable=False)

    # Relation avec Connection via User_Connection (Many-to-Many)
    connections = relationship("Connection", secondary="User_Connection", back_populates="users", passive_deletes=True)

    # Relation avec Portfolio (One-to-Many)
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
