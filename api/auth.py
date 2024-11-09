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

    if is_username_valid(username) and is_password_valid(password):
        user = UserRepository().login(username=username, password=password)
        if user:
            logging.info(user.username)
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Please enter a valid email and a strong password"
    )


@auth_router.post("/register")
async def register(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    username = form_data.username
    password = form_data.password

    user = UserRepository().create(username=username, password=password)
    logging.info(user.id)
    logging.info(user.username)
    
