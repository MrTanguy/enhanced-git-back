import logging
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, status, Form

from models.connection import Connection
from repositories.connection_repository import ConnectionRepository
from services.security.bearer import Bearer
from services.security.data import Data
from utils.utils import init_website_service

connection_router = APIRouter()
load_dotenv()


@connection_router.get("/url")
async def get_oauth_url(
    _: Annotated[int, Depends(Bearer().get_user_id)],
    website: str
):
    """
    Return the OAuth URL for the requested website.

    :param user_id: ID of the authenticated user (unused but required for auth)
    :param website: Target website (e.g., github, gitlab)

    :return: An OAuth authorization URL
    """
    service = init_website_service(website=website)
    return service.get_oauth_url()


@connection_router.post("/token")
async def connect_with_token(
    user_id: Annotated[int, Depends(Bearer().get_user_id)],
    code: Annotated[str, Form()],
    website: Annotated[str, Form()]
):
    """
    Connect a user using an OAuth token and store the connection.

    :param user_id: ID of the authenticated user
    :param code: OAuth authorization code
    :param website: Target OAuth service

    :return: Success message on connection
    """
    try:
        service = init_website_service(website=website)
        data = service.get_access_token(code=code)

        security = Data()
        access_token = data['access_token']
        if website == 'gitlab':
            refresh_token = data['refresh_token']
        else:
            refresh_token = None

        # On crée une fausse connection le temps de récupérer les informations
        new_connection = Connection()
        new_connection.access_token = security.encrypt(access_token)
        new_connection.refresh_token = security.encrypt(refresh_token)

        user_info = service.get_user_info(new_connection)
        account_id = user_info["id"]

        ConnectionRepository().create(
            user_id=user_id,
            website=website,
            access_token=access_token,
            account_id=account_id,
            refresh_token=refresh_token
        )

        return {"message": "Successfully connected."}

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during the OAuth token process"
        ) from e


@connection_router.delete("/delete/{connection_id}")
async def delete_connection(
    user_id: Annotated[int, Depends(Bearer().get_user_id)],
    connection_id: int
):
    """
    Delete a user's connection to a third-party website.

    :param user_id: ID of the authenticated user
    :param connection_id: ID of the connection to delete
    """
    try:
        ConnectionRepository().delete(user_id, connection_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during the process"
        ) from e


@connection_router.get("/projects")
async def get_all_projects(
    user_id: Annotated[int, Depends(Bearer().get_user_id)],
    account_id: int,
    website: str
):
    """
    Fetch all public projects for a connected account.

    :param user_id: ID of the authenticated user
    :param account_id: ID of the external account
    :param website: Website associated with the connection

    :return: List of public projects
    """
    connections = ConnectionRepository().read(user_id=user_id)
    service = init_website_service(website=website)

    is_owner = any(
        c.account_id == account_id and c.website == website
        for c in connections
    )

    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This isn't a connected account."
        )

    all_publics = service.get_all_public_projects(account_id=account_id)
    return all_publics
