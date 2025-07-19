"""
Repository to manage user CRUD operations in the database.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from models.user import User
from services.db.db import DB


class UserRepository:
    """Manage CRUD operations for User model."""

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

        :return: user's data or raises HTTPException on error
        """
        try:
            with self.db_connection.get_connection() as session:
                hashed_password = self.db_connection.pwd_context.hash(password)
                new_user = User(username=username, password=hashed_password, is_active=True)
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                return new_user
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists."
            ) from exc
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            ) from e

    ########
    # Read #
    ########
    def read_by_id(self, _id: int) -> User:
        """
        Try to find the user in DB according to his id

        :param _id: the id to find

        :return: the User or raises HTTPException if not found
        """
        with self.db_connection.get_connection() as session:
            cmd = select(User).options(joinedload(User.connections), joinedload(User.portfolios)).filter_by(id=_id)
            user = session.execute(cmd).unique().scalar_one_or_none()
            if user:
                return user
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {_id} not found."
            )

    def read_by_username(self, username: str) -> User | None:
        """
        Try to find the user in DB according to his username

        :param username: the email address to find

        :return: the User or None
        """
        with self.db_connection.get_connection() as session:
            cmd = select(User).filter_by(username=username)
            user = session.execute(cmd).scalar_one_or_none()
            return user

    def login(self, username: str, password: str) -> User | None:
        """
        Check if the user and password are correct

        :param username: user's email address
        :param password: user's password

        :return: user's data or None if invalid credentials
        """
        try:
            db_user = self.read_by_username(username=username)

            # If we have a user and the password is correct
            if db_user and self.db_connection.pwd_context.verify(password, db_user.password):
                return db_user
            return None
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            ) from e

    ##########
    # Update #
    ##########
    def update(self, user: User):
        """
        Update an existing user.

        :param user: User object with updated fields
        """
        try:
            with self.db_connection.get_connection() as session:
                # Ensure password is hashed if modified
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
            ) from e

    ##########
    # Delete #
    ##########
    def delete(self, _id: int):
        """
        Delete user by id

        :param _id: User id to delete
        """
        try:
            with self.db_connection.get_connection() as session:
                cmd = delete(User).filter_by(id=_id)
                result = session.execute(cmd)
                if result.rowcount == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User {_id} not found."
                    )
                session.commit()
        except HTTPException:
            raise
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error."
            ) from e
