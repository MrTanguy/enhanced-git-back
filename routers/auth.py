"""Authentication routes for the Enhanced-git API."""

import logging
from typing import Annotated

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, status, Response, Request

from services.security.bearer import Bearer
from services.security.refresh import Refresh
from repositories.user_repository import UserRepository
from utils.utils import is_username_valid, is_password_valid

auth_router = APIRouter()
load_dotenv()


@auth_router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response
):
    """
    Authenticate the user and return bearer and refresh tokens.

    :param form_data: The user's credentials (x-www-form-urlencoded)
    :param response: The HTTP response

    :return: A bearer token and a refresh token in HttpOnly cookie
    """
    username = form_data.username
    password = form_data.password

    if not is_username_valid(username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please enter a valid email address"
        )

    if not is_password_valid(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please enter a strong password"
        )

    try:
        user = UserRepository().login(username=username, password=password)
        if user:
            bearer_token = Bearer().generate(user_id=user.id)
            refresh_token_value  = Refresh().generate(user_id=user.id)

            response.set_cookie(
                key="refresh",
                value=refresh_token_value,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=604800
            )

            return {"bearer": bearer_token}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except HTTPException:
        raise
    except Exception as error:
        logging.exception("Error while logging in user %s: %s", username, str(error))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from error


@auth_router.post("/register")
async def register(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response
):
    """
    Register the user and return bearer and refresh tokens.

    :param form_data: The user's credentials (x-www-form-urlencoded)
    :param response: The HTTP response

    :return: A bearer token and a refresh token in HttpOnly cookie
    """
    username = form_data.username
    password = form_data.password

    if not is_username_valid(username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please enter a valid email address"
        )

    if not is_password_valid(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please enter a strong password"
        )

    user = UserRepository().create(username=username, password=password)
    if user:
        bearer_token = Bearer().generate(user_id=user.id)
        refresh_token_value = Refresh().generate(user_id=user.id)

        response.set_cookie(
            key="refresh",
            value=refresh_token_value,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=604800
        )

        return {"bearer": bearer_token}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Please enter a valid email address and a strong password"
    )


@auth_router.get("/refresh")
async def refresh_token(request: Request):
    """
    Send back a new bearer token using the refresh token from cookie.

    :param request: The HTTP request containing the refresh token cookie

    :return: A new bearer token
    """
    refresh_cookie = request.cookies.get("refresh")
    if not refresh_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing"
        )

    user_id = Refresh().verify(token=refresh_cookie)
    bearer_token = Bearer().generate(user_id=user_id)
    return {"bearer": bearer_token}
