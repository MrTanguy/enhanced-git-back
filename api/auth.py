import os
import logging

from typing import Annotated
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException,  Depends, status, Response, Cookie, Request
from fastapi.security import OAuth2PasswordRequestForm

from repositories.UserRepository import UserRepository
from services.security.bearer import Bearer
from services.security.refresh import Refresh
from utils.utils import is_username_valid, is_password_valid

auth_router = APIRouter()
load_dotenv()


@auth_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    """
    Authenticate the user and return bearer and refresh tokens.

    :param form_data: The data's user (x-www-form-urlencoded)
    :param response: The http response

    :return: A bearer token and a refresh token in HttpOnly cookie
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
                samesite="None",
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
    """
    Register the user and return bearer and refresh tokens.

    :param form_data: The data's user (x-www-form-urlencoded)
    :param response: The http response

    :return: A bearer token and a refresh token in HttpOnly cookie
    """

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
                samesite="None",
                max_age=604800
            )

            return {"bearer": bearer}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Please enter a valid email address and a strong password"
    )
    

@auth_router.get("/refresh")
async def refresh(request: Request):
    """
    Send back a new bearer token

    :param request: the http request used to get the refresh token in HttpOnly

    :return: A bearer token
    """

    refresh_token = request.cookies.get("refresh")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing"
        )

    id = Refresh().verify(token=refresh_token)
    if id:
        bearer = Bearer().generate(_id=id)
        return {"bearer": bearer}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token"
    )


@auth_router.get("/oauthurl")
async def get_oauthurl(token: Annotated[str, Depends(Bearer().oauth2_scheme)], website: str):
    
    test = Bearer().verify(token=token)
    if test:
        if website == 'github':
            client_id = os.getenv("GITHUB_CLIENT")
            url_callback = os.getenv("GITHUB_CALLBACK")
            return f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={url_callback}&scope=user"
        elif website == 'gitlab':
            pass
        else:
            pass