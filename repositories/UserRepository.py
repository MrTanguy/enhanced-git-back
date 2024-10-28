import logging

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

    def read(self, _id: int) -> User:
        with self.db_connection.get_connection() as session:
            cmd = select(User).filter_by(id=_id)
            user_row = session.execute(cmd)
            user = user_row.scalar_one_or_none()
            if user:
                return user
            else:
                raise ValueError(f"User with id {_id} not found")

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
        with self.db_connection.get_connection() as session:
            try:
                logging.info(f"Tentative de connexion pour l'utilisateur : {username}")
                stmt = select(User).filter_by(username=username)
                db_user = session.execute(stmt).scalar_one()

                if self.db_connection.pwd_context.verify(password, db_user.password):
                    return db_user
                else:
                    return None

            except NoResultFound:
                logging.info("Aucun résultat trouvé")
                return None
            except Exception as e:
                logging.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
                return None
