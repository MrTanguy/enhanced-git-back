import logging

from fastapi import HTTPException, status
from sqlalchemy import select, delete, update
from sqlalchemy.exc import NoResultFound

from models.user import User
from services.db.db import DB


class UserRepository:
    def __init__(self):
        self.db_connection = DB()

    def create(self, username: str, password: str) -> User:
        """Crée un nouvel utilisateur avec un mot de passe haché."""
        with self.db_connection.get_connection() as session:
            hashed_password = self.db_connection.pwd_context.hash(password)
            new_user = User(username=username, password=hashed_password, is_active=True)
            session.add(new_user)
            session.commit()
            return new_user

    def read_by_id(self, _id: int) -> User:
        with self.db_connection.get_connection() as session:
            cmd = select(User).filter_by(id=_id)
            user_row = session.execute(cmd)
            user = user_row.scalar_one_or_none()
            if user:
                return user
            raise ValueError(f"User with id {_id} not found")
        
    def read_by_username(self, username: str) -> User:
        with self.db_connection.get_connection() as session:
            cmd = select(User).filter_by(username=username)
            user_row = session.execute(cmd)
            user = user_row.scalar_one_or_none()
            if user:
                return user
            raise ValueError(f"User with username {username} not found")

    def update(self, user: User):
        """Met à jour un utilisateur existant."""
        with self.db_connection.get_connection() as session:
            cmd = (
                update(User)
                .filter_by(id=user.id)
                .values(username=user.username, password=user.password, is_active=user.is_active)
            )
            session.execute(cmd)
            session.commit()

    def delete(self, _id: int):
        with self.db_connection.get_connection() as session:
            cmd = delete(User).filter_by(id=_id)
            session.execute(cmd)
            session.commit()

    def login(self, username: str, password: str):
        """Récupère un utilisateur par nom d'utilisateur et vérifie le mot de passe."""
        try:
            logging.info(f"Tentative de connexion pour l'utilisateur : {username}")
            db_user = self.read_by_username(username=username)

            if self.db_connection.pwd_context.verify(password, db_user.password):
                return db_user
            else:
                return None
        except NoResultFound:
            return None
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
