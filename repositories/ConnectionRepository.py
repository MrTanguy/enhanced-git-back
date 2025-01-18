import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.connection import Connection
from models.user import User
from services.db.db import DB


class ConnectionRepository:
    def __init__(self):
        self.db_connection = DB()

    ##########
    # Create #
    ##########
    def create(self, id: int, website: str, access_token: str, account_id: int, service):
        try:
            with self.db_connection.get_connection() as session:
                # Find the user by ID
                find_user = select(User).filter_by(id=id)
                user = session.execute(find_user).scalar_one_or_none()
                if user:
                    # Check if the account_id isn't already associated with the user
                    if any(connection.account_id == account_id and connection.website == website for connection in user.connections):
                        # Find the existing connection and update the access_token
                        find_connection = select(Connection).filter_by(website=website, account_id=account_id)
                        connection = session.execute(find_connection).scalar_one_or_none()
                        if connection:
                            old_access_token = connection.access_token
                            connection.access_token = access_token
                            session.commit()
                            service.deleteAccessToken(access_token=old_access_token)
                            raise HTTPException(
                                status_code=status.HTTP_208_ALREADY_REPORTED,
                                detail="User already connected"
                            )
                    else:
                        # Create a new connection
                        new_connection = Connection(account_id=account_id, website=website, access_token=access_token)
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
