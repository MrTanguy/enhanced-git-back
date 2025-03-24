from sqlalchemy import Column, ForeignKey, Integer, String
from services.db.base import Base


class Portfolio_Connection(Base):
    __tablename__ = 'Portfolio_Connection'

    portfolio_id = Column(String(26), ForeignKey('Portfolio.uuid', ondelete="CASCADE"), primary_key=True)
    connection_id = Column(Integer, ForeignKey('Connection.id', ondelete="CASCADE"), primary_key=True)
