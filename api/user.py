import logging

from typing import Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, status

from repositories.UserRepository import UserRepository
from services.security.bearer import Bearer
from utils.utils import init_website_service

user_router = APIRouter()
load_dotenv()

@user_router.get("/data")
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
