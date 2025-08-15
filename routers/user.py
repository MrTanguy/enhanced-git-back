import logging

from typing import Optional, Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, status, Query

from repositories.user_repository import UserRepository
from services.security.bearer import Bearer
from utils.utils import init_website_service

user_router = APIRouter()
load_dotenv()


@user_router.get("/data")
async def get_user_data(
    user_id: Annotated[int, Depends(Bearer().get_user_id)],
    types: Optional[str] = Query(None, description="Comma-separated values: connections,portfolios")
):
    """
    Retrieve user data such as connections and portfolios based on the specified types.

    :param user_id: The ID of the authenticated user
    :param types: Optional query param (comma-separated) to filter data types: connections, portfolios
    :return: Dictionary containing the requested user data
    """
    try:
        modes = ["connections", "portfolios"]
        if types:
            arguments = types.lower().split(",")
            for argument in arguments:
                if argument not in modes:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unknown type: {argument}"
                    )
        else:
            arguments = modes

        user_data = UserRepository().read_by_id(user_id)
        result = {}

        if "connections" in arguments:
            result["connections"] = []
            result["errors"] = []
            for connection in user_data.connections:
                service = init_website_service(website=connection.website)
                try:
                    user_info = service.get_user_info(connection=connection)
                except HTTPException as e:
                    result["errors"].append(e.detail)
                    continue

                if connection.website == "github":
                    username = user_info['login']
                elif connection.website == "gitlab":
                    username = user_info['username']
                else:
                    raise ValueError(f"Unable to find the website : {connection.website}")

                result["connections"].append({
                    "website": connection.website,
                    "id": connection.account_id,
                    "username": username
                })

        if "portfolios" in arguments:
            result["portfolios"] = []
            for portfolio in user_data.portfolios:
                result["portfolios"].append({
                    "uuid": portfolio.uuid,
                    "title": portfolio.title,
                    "content": portfolio.content
                })

        return result

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred"
        ) from e

@user_router.get("/me")
async def get_user_info(
    user_id: Annotated[int, Depends(Bearer().get_user_id)]
):
    """
    Retrieve the id of the user

    :param user_id: The ID of the authenticated user
    """
    return {"id": user_id}
