from sqlalchemy import Column, ForeignKey, INTEGER
from services.db.base import Base

class User_Connection(Base):
    __tablename__ = 'User_Connection'

    user_id = Column(INTEGER, ForeignKey('User.id'), primary_key=True)
    connection_id = Column(INTEGER, ForeignKey('Connection.id'), primary_key=True)
