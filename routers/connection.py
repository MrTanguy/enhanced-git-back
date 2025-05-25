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
async def get_oauth_url(user_id: Annotated[int, Depends(Bearer().get_user_id)], website: str):
    """
    Send back the oauth url depending the website asked

    :param token: Bearer token
    :param website: website asked

    :return: an url
    """

    service = init_website_service(website=website)
    return service.getOauthUrl()


@connection_router.post("/token")
async def connect_with_token(user_id: Annotated[int, Depends(Bearer().get_user_id)], code: Annotated[str, Form()], website: Annotated[str, Form()]):
    try:
        service = init_website_service(website=website)
        access_token = service.getAccessToken(code=code)
        
        user_info = service.getUserInfo(access_token=access_token)
        account_id = user_info['id']
        
        ConnectionRepository().create(user_id=user_id, website=website, access_token=access_token, account_id=account_id, service=service)
        
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
async def delete_connection(user_id: Annotated[int, Depends(Bearer().get_user_id)], connection_id: int):
    try:
        ConnectionRepository().delete(user_id, connection_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during the process"
        )

@connection_router.get("/projects")
async def get_all_projects(user_id: Annotated[int, Depends(Bearer().get_user_id)], account_id: int, website: str):
    connections = ConnectionRepository().read(user_id=user_id)

    isOwner = any(c.account_id == account_id and c.website == website for c in connections)

    if not isOwner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't a connected account."
        )

    service = init_website_service(website=website)
    all_publics = service.getAllPublicProjects(account_id=account_id)
    return all_publics
