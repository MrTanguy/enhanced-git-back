import logging

from typing import Annotated

from fastapi import APIRouter, HTTPException,  Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from repositories.UserRepository import UserRepository
from utils.utils import is_username_valid, is_password_valid

auth_router = APIRouter()


@auth_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    username = form_data.username
    password = form_data.password

    if is_username_valid(username=username) and is_password_valid(password=password):
        user = UserRepository().login(username=username, password=password)
        if user:
            logging.info(user.username)
            return user
    # The user and/or password don't match the regex
    # The username isn't find in the DB
    # The password is incorrect
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid credentials"
    )


@auth_router.post("/register")
async def register(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    username = form_data.username
    password = form_data.password

    if is_username_valid(username=username) and is_password_valid(password=password):
        user = UserRepository().create(username=username, password=password)
        if user:
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Please enter a valid email address and a strong password"
    )
    
