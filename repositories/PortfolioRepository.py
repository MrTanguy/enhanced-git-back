import logging
from fastapi import HTTPException, status
from sqlalchemy import select
from ulid import ulid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from models.portfolio import Portfolio
from services.db.db import DB


class PortfolioRepository:
    def __init__(self):
        self.db_connection = DB()

    def create(self, user_id: int):
        try:
            with self.db_connection.get_connection() as session:
                # Boucle infini si l'ULID existe déjà
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occured while creating a portfolio"
            )
        
    def get_by_ulid(self, ulid: str):
        try:
            with self.db_connection.get_connection() as session:
                cmd = select(Portfolio).filter_by(uuid=ulid)
                portfolio = session.execute(cmd).scalar_one_or_none()
                if portfolio:
                    return portfolio
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Unable to find the portfolio with the ulid: {ulid}"
                )
        except HTTPException as e:
            raise
        except Exception as e:
            logging.error(f"Erreur lors de la récupération d'un portfolio: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        

    def update(self, ulid: str, update_data: dict):
        try:
            with self.db_connection.get_connection() as session:

                portfolio = session.execute(select(Portfolio).filter_by(uuid=ulid)).scalar_one_or_none()
                if not portfolio:
                    raise HTTPException(status_code=404, detail="Portfolio not found")

                for key, value in update_data.dict(exclude_unset=True).items():
                    setattr(portfolio, key, value)

                session.commit()
                session.refresh(portfolio)
                
                return portfolio
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour du portfolio: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
