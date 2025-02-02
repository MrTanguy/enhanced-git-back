from sqlalchemy import Column, INTEGER, VARCHAR
from sqlalchemy.orm import relationship
from services.db.base import Base


class Connection(Base):
    __tablename__ = 'Connection'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    account_id = Column(INTEGER, nullable=False)
    website = Column(VARCHAR(20), nullable=False)
    access_token = Column(VARCHAR(50), nullable=False)
    users = relationship("User", secondary="User_Connection", back_populates="connections")

