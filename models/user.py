from sqlalchemy import Column, INTEGER, VARCHAR, BOOLEAN
from sqlalchemy.orm import declarative_base


class User(declarative_base()):
    __tablename__ = 'User'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    username = Column(VARCHAR(255), nullable=False, unique=True)
    password = Column(VARCHAR(255), nullable=False)
    is_active = Column(BOOLEAN, nullable=False)
