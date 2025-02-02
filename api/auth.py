import logging

from typing import Annotated
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, status, Response, Request, Form

from repositories.UserRepository import UserRepository
from repositories.ConnectionRepository import ConnectionRepository
from services.security.bearer import Bearer
from services.security.refresh import Refresh
from utils.utils import is_username_valid, is_password_valid, init_website_service

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
        try:
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
        except Exception:
            raise
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
    bearer = Bearer().generate(_id=id)
    return {"bearer": bearer}
