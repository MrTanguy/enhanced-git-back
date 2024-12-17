import logging

from typing import Annotated

from fastapi import APIRouter, HTTPException,  Depends, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm

from repositories.UserRepository import UserRepository
from services.security.bearer import Bearer
from services.security.refresh import Refresh
from utils.utils import is_username_valid, is_password_valid

auth_router = APIRouter()


@auth_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    """
    Authenticate the user and return access and refresh tokens.

    :param form_data: The data's user (x-www-form-urlencoded)

    :return: # TODO : Que renvoie cette fonction ? 
    """

    username = form_data.username
    password = form_data.password

    if is_username_valid(username=username) and is_password_valid(password=password):
        user = UserRepository().login(username=username, password=password)
        if user:
            bearer = Bearer().generate(_id=user.id)
            refresh = Refresh().generate(_id=user.id)

            response.set_cookie(
                key="refresh",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=604800
            )

            return {"bearer": bearer}
    # The user and/or password don't match the regex
    # The username isn't find in the DB
    # The password is incorrect
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid credentials"
    )

@auth_router.post("/register")
async def register(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):

    username = form_data.username
    password = form_data.password

    if is_username_valid(username=username) and is_password_valid(password=password):
        user = UserRepository().create(username=username, password=password)
        if user:
            bearer = Bearer().generate(_id=user.id)
            refresh = Refresh().generate(_id=user.id)

            response.set_cookie(
                key="refresh",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=604800
            )

            return {"bearer": bearer}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Please enter a valid email address and a strong password"
    )
    

@auth_router.get("/refresh")
async def refresh(token: Annotated[str, Depends(Bearer().oauth2_scheme)]):
    id = Refresh().verify(token=token)
    if id:
        bearer = Bearer().generate(_id=id) 
        return {"bearer": bearer}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid or expired refresh token"
    )
    