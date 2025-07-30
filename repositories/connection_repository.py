import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.connection import Connection
from models.user_connection import User_Connection
from models.user import User
from services.db.db import DB


class ConnectionRepository:
    """Manages CRUD operations for user connections."""

    def __init__(self):
        self.db_connection = DB()

    ##########
    # Create #
    ##########
    def create(self, user_id: int, website: str, access_token: str, account_id: int):
        """
        Create or link a connection for a user.

        :param user_id: ID of the user
        :param website: website/service name
        :param access_token: token to access the service
        :param account_id: external account ID
        """
        try:
            with self.db_connection.get_connection() as session:
                find_user = select(User).filter_by(id=user_id)
                user = session.execute(find_user).scalar_one_or_none()

                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found."
                    )

                find_connection = select(Connection).filter_by(account_id=account_id)
                connection = session.execute(find_connection).scalar_one_or_none()

                if connection:
                    find_jointure = select(User_Connection).filter_by(
                        user_id=user_id, connection_id=connection.id
                    )
                    jointure = session.execute(find_jointure).scalar_one_or_none()

                    if jointure:
                        raise HTTPException(
                            status_code=status.HTTP_208_ALREADY_REPORTED,
                            detail="User already connected"
                        )

                    user.connections.append(connection)
                    session.commit()

                else:
                    new_connection = Connection(
                        account_id=account_id, website=website, access_token=access_token
                    )
                    user.connections.append(new_connection)
                    session.add(new_connection)
                    session.commit()

        except HTTPException:
            raise
        except IntegrityError as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Integrity error, possible duplicate connection."
            ) from e
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            ) from e

    ########
    # Read #
    ########
    def read(self, user_id: int):
        """
        Read all connections linked to a user.

        :param user_id: ID of the user
        :return: list of Connection objects or empty list
        """
        try:
            with self.db_connection.get_connection() as session:
                find_user = select(User).filter_by(id=user_id)
                user = session.execute(find_user).scalar_one_or_none()

                if user:
                    return user.connections
                return []

        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            ) from e

    ##########
    # Delete #
    ##########
    def delete(self, user_id: int, account_id: int):
        """
        Delete a connection link for a user and possibly the connection itself.

        :param user_id: ID of the user
        :param account_id: external account ID
        :return: success message dict
        """
        try:
            with self.db_connection.get_connection() as session:
                find_connection = select(Connection).filter_by(account_id=account_id)
                connection = session.execute(find_connection).scalar_one_or_none()

                if not connection:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Connection not found."
                    )

                find_jointure = select(User_Connection).filter_by(
                    user_id=user_id, connection_id=connection.id
                )
                jointure = session.execute(find_jointure).scalar_one_or_none()

                if not jointure:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User-Connection relation not found."
                    )

                session.delete(jointure)
                session.commit()

                remaining_connections = (
                    session.query(User_Connection)
                    .filter(User_Connection.connection_id == connection.id)
                    .count()
                )

                if remaining_connections == 0:
                    session.delete(connection)
                    session.commit()

                return {"message": "Connection deleted successfully."}

        except HTTPException:
            raise
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            ) from e
