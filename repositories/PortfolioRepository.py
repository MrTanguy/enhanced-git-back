import logging
from ulid import ulid
from sqlalchemy.exc import IntegrityError

from models.portfolio import Portfolio
from services.db.db import DB


class PortfolioRepository:
    def __init__(self):
        self.db_connection = DB()

    def create(self, user_id: int):
        try:
            with self.db_connection.get_connection() as session:
                while True:
                    try:
                        new_portfolio = Portfolio(user_id=user_id, title="New Portfolio", description="")
                        session.add(new_portfolio)
                        session.commit()
                        session.refresh(new_portfolio)
                        break 
                    except IntegrityError:
                        session.rollback()
                        new_portfolio.uuid = str(ulid())
                
                return new_portfolio
        except Exception as e:
            logging.error(f"Erreur lors de la création du portfolio: {e}")
            return None