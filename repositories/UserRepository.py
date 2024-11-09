import logging

from fastapi import HTTPException, status
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError

from models.user import User
from services.db.db import DB


class UserRepository:
    def __init__(self):
        self.db_connection = DB()

    ##########
    # Create #
    ##########
    def create(self, username: str, password: str) -> User:
        """
        Create a new user

        :param username: user's email address
        :param password: user's password

        :return: user's data or Error
        """
        try:
            with self.db_connection.get_connection() as session:
                hashed_password = self.db_connection.pwd_context.hash(password)
                new_user = User(username=username, password=hashed_password, is_active=True)
                session.add(new_user)
                session.commit()
                session.refresh(new_user)  # Recharge les données de l'utilisateur
                return new_user
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists."
            )
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            )

    ########
    # Read #
    ########
    def read_by_id(self, _id: int) -> User:
        try:
            with self.db_connection.get_connection() as session:
                cmd = select(User).filter_by(id=_id)
                user = session.execute(cmd).scalar_one_or_none()
                if user:
                    return user
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Utilisateur avec l'id {_id} non trouvé"
                )
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            )
        
    def read_by_username(self, username: str) -> User:
        with self.db_connection.get_connection() as session:
            cmd = select(User).filter_by(username=username)
            user = session.execute(cmd).scalar_one_or_none()
            if user:
                return user

    def login(self, username: str, password: str) -> User:
        """
        Check if the user and password are correct

        :param username: user's email address
        :param password: user's password

        :return: user's data or Error
        """
        try:
            logging.info(f"Username : {username}")
            db_user = self.read_by_username(username=username)

            # If we have a user and the password is correct
            if db_user and self.db_connection.pwd_context.verify(password, db_user.password):
                return db_user
            # None in any other cases
        # Error with the DB
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            )

    ##########
    # Update #
    ##########
    def update(self, user: User):
        """Met à jour un utilisateur existant."""
        try:
            with self.db_connection.get_connection() as session:
                # Assure que le mot de passe est rehashé si modifié
                if user.password:
                    user.password = self.db_connection.pwd_context.hash(user.password)
                cmd = (
                    update(User)
                    .filter_by(id=user.id)
                    .values(username=user.username, password=user.password, is_active=user.is_active)
                )
                session.execute(cmd)
                session.commit()
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            )

    ##########
    # Delete #
    ##########
    def delete(self, _id: int):
        try:
            with self.db_connection.get_connection() as session:
                cmd = delete(User).filter_by(id=_id)
                result = session.execute(cmd)
                if result.rowcount == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Utilisateur avec l'id {_id} non trouvé."
                    )
                session.commit()
        except HTTPException:
            raise
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            )
