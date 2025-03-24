from sqlalchemy import Column, ForeignKey, Integer
from services.db.base import Base


class User_Connection(Base):
    __tablename__ = 'User_Connection'

    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), primary_key=True)
    connection_id = Column(Integer, ForeignKey('Connection.id', ondelete="CASCADE"), primary_key=True)
