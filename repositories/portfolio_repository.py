import logging
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from ulid import ulid
from fastapi import HTTPException, status

from models.portfolio import Portfolio
from services.db.db import DB


class PortfolioRepository:
    """Class to handle database operations for Portfolio objects."""

    def __init__(self):
        self.db_connection = DB()

    def create(self, user_id: int) -> Portfolio:
        """Create a new portfolio for the given user."""
        try:
            with self.db_connection.get_connection() as session:
                # Boucle infinie si l'uuid existe déjà
                while True:
                    try:
                        new_portfolio = Portfolio(user_id=user_id, title="New Portfolio", content=[])
                        session.add(new_portfolio)
                        session.commit()
                        session.refresh(new_portfolio)
                        break
                    except IntegrityError:
                        session.rollback()
                        new_portfolio.uuid = str(ulid())
                return new_portfolio
        except Exception as e:
            logging.error("Erreur lors de la création du portfolio: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occured while creating a portfolio"
            ) from e

    def get_by_uuid(self, uuid: str) -> Portfolio:
        """Retrieve a portfolio by its UUID."""
        try:
            with self.db_connection.get_connection() as session:
                cmd = select(Portfolio).filter_by(uuid=uuid)
                portfolio = session.execute(cmd).scalar_one_or_none()
                if portfolio:
                    return portfolio
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Portfolio not found"
                )
        except HTTPException:
            raise
        except Exception as e:
            logging.error("Erreur lors de la récupération d'un portfolio: %s", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") from e

    def update(self, uuid: str, update_data: dict) -> Portfolio:
        """Update an existing portfolio identified by UUID with given data."""
        try:
            with self.db_connection.get_connection() as session:
                portfolio = session.execute(select(Portfolio).filter_by(uuid=uuid)).scalar_one_or_none()
                if not portfolio:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Portfolio not found"
                    )
                for key, value in update_data.dict(exclude_unset=True).items():
                    setattr(portfolio, key, value)

                session.commit()
                session.refresh(portfolio)

                return portfolio
        except HTTPException:
            raise
        except Exception as e:
            logging.error("Erreur lors de la mise à jour du portfolio: %s", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") from e

    def delete(self, uuid: str):
        """Delete a portfolio by its UUID."""
        try:
            with self.db_connection.get_connection() as session:
                cmd = delete(Portfolio).filter_by(uuid=uuid)
                session.execute(cmd)
                session.commit()
        except Exception as e:
            logging.error("Erreur lors de la suppression du portfolio: %s", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") from e
