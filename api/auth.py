import logging

from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from repositories.UserRepository import UserRepository

auth_router = APIRouter()


@auth_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    username = form_data.username
    password = form_data.password

    user = UserRepository().login(username=username, password=password)
    if user:
        logging.info(user.username)
        return user
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@auth_router.post("/register")
async def register(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    username = form_data.username
    password = form_data.password

    user = UserRepository().create(username=username, password=password)
    logging.info(user.id)
    logging.info(user.username)
    
