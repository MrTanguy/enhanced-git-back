import logging

from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from models.connection import Connection
from models.user_connection import User_Connection
from models.user import User
from services.db.db import DB


class ConnectionRepository:
    def __init__(self):
        self.db_connection = DB()

    ##########
    # Create #
    ##########
    def create(self, user_id: int, website: str, access_token: str, account_id: int, service):

        try:
            with self.db_connection.get_connection() as session:
                # Find the user
                find_user = select(User).filter_by(id=user_id)
                user = session.execute(find_user).scalar_one_or_none()
                if user:
                    # Find the account
                    find_connection = select(Connection).filter_by(account_id=account_id)
                    connection = session.execute(find_connection).scalar_one_or_none()
                    if connection:
                        # The connection is already in the DB
                        find_jointure = select(User_Connection).filter_by(user_id=user_id, connection_id=connection.id)
                        jointure = session.execute(find_jointure).scalar_one_or_none()
                        if jointure:
                            # Connection already linked
                            raise HTTPException(
                                status_code=status.HTTP_208_ALREADY_REPORTED,
                                detail="User already connected"
                            )
                        else:
                            # Link the user and the connection in User_Connection
                            user.connections.append(connection)
                            session.commit()
                    else:
                        # The account isn't in the DB
                        # Create the Connection
                        new_connection = Connection(account_id=account_id, website=website, access_token=access_token)
                        # Link the user and the connection in User_Connection
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
            )
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            )
        
    def delete(self, user_id, account_id):
        try:
            with self.db_connection.get_connection() as session:
                # Find the connection
                find_connection = select(Connection).filter_by(account_id=account_id)
                connection = session.execute(find_connection).scalar_one_or_none()

                if connection:
                    # Find the jointure
                    find_jointure = select(User_Connection).filter_by(user_id=user_id, connection_id=connection.id)
                    jointure = session.execute(find_jointure).scalar_one_or_none()

                    # Delete the jointure if exists
                    if jointure:
                        session.delete(jointure)
                        session.commit()
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="User-Connection relation not found."
                        )

                    # Check if there are other users using this connection
                    remaining_connections = (
                        session.query(User_Connection)
                        .filter(User_Connection.connection_id == connection.id)
                        .count()
                    )

                    if remaining_connections == 0:
                        # If no users are left, delete the connection
                        session.delete(connection)
                        session.commit()

                    return {"message": "Connection deleted successfully."}

                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Connection not found."
                    )

        except HTTPException:
            raise
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            )

