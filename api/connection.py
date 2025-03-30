import logging

from typing import Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, status, Form

from repositories.ConnectionRepository import ConnectionRepository
from services.security.bearer import Bearer
from utils.utils import init_website_service

connection_router = APIRouter()
load_dotenv()

@connection_router.get("/url")
async def get_oauth_url(token: Annotated[str, Depends(Bearer().oauth2_scheme)], website: str):
    """
    Send back the oauth url depending the website asked

    :param token: Bearer token
    :param website: website asked

    :return: an url
    """
    Bearer().verify(token=token)
    service = init_website_service(website=website)
    return service.getOauthUrl()


@connection_router.post("/token")
async def connect_with_token(token: Annotated[str, Depends(Bearer().oauth2_scheme)], code: Annotated[str, Form()], website: Annotated[str, Form()]):
    try:
        id = Bearer().verify(token=token)['id']

        service = init_website_service(website=website)
        access_token = service.getAccessToken(code=code)
        
        user_info = service.getUserInfo(access_token=access_token)
        account_id = user_info['id']
        
        ConnectionRepository().create(user_id=id, website=website, access_token=access_token, account_id=account_id, service=service)
        
        return {"message": "Successfully connected."}

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during the OAuth token process"
        )

@connection_router.delete("/delete/{connection_id}")
async def delete_connection(token: Annotated[str, Depends(Bearer().oauth2_scheme)], connection_id: int):
    try:
        id = Bearer().verify(token=token)['id']
        ConnectionRepository().delete(id, connection_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during the process"
        )
