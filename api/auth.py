import logging

from typing import Annotated
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends, status, Response, Request, Form
from fastapi.security import OAuth2PasswordRequestForm

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


@auth_router.get("/oauthurl")
async def get_oauthurl(token: Annotated[str, Depends(Bearer().oauth2_scheme)], website: str):
    """
    Send back the oauth url depending the website asked

    :param token: Bearer token
    :param website: website asked

    :return: an url
    """
    Bearer().verify(token=token)
    service = init_website_service(website=website)
    return service.getOauthUrl()


@auth_router.post("/oauthtoken")
async def get_oauthtoken(token: Annotated[str, Depends(Bearer().oauth2_scheme)], code: Annotated[str, Form()], website: Annotated[str, Form()]):
    try:
        id = Bearer().verify(token=token)['id']

        service = init_website_service(website=website)
        access_token = service.getAccessToken(code=code)
        
        user_info = service.getUserInfo(access_token=access_token)
        account_id = user_info['id']
        
        ConnectionRepository().create(id=id, website=website, access_token=access_token, account_id=account_id, service=service)
        
        return {"message": "Successfully connected."}

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during the OAuth token process"
        )
    
@auth_router.get("/userdata")
async def get_user_data(token: Annotated[str, Depends(Bearer().oauth2_scheme)]):
    try:
        id = Bearer().verify(token=token)['id']

        user_data = UserRepository().read_by_id(id)

        result = {"connections": []}

        for connection in user_data.connections:
            service = init_website_service(website=connection.website)
            username = service.getUserInfo(access_token=connection.access_token)['login']

            connection_result = {"website": connection.website,
                                 "id": connection.account_id,
                                 "username": username}
            
            result["connections"].append(connection_result)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred"
        )