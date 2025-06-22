import logging

from typing import List, Optional, Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, status, Query

from repositories.UserRepository import UserRepository
from services.security.bearer import Bearer
from utils.utils import init_website_service

user_router = APIRouter()
load_dotenv()

@user_router.get("/data")
async def get_user_data( 
    user_id: Annotated[int, Depends(Bearer().get_user_id)],  
    types: Optional[str] = Query(None, description="Comma-separated values: connections,portfolios")
):
    try:
        modes = ["connections", "portfolios"]
        if types:
            arguments = types.lower().split(",")

            for argument in arguments:
                if argument not in modes:
                    raise HTTPException(status_code=400, detail=f"Unknown type: {argument}")
        else:
            arguments = modes

        user_data = UserRepository().read_by_id(user_id)

        result = {}

        if "connections" in arguments:
            result["connections"] = []
            for connection in user_data.connections:
                service = init_website_service(website=connection.website)
                username = service.getUserInfo(access_token=connection.access_token)['login']

                connection_result = {
                    "website": connection.website,
                    "id": connection.account_id,
                    "username": username
                }
                result["connections"].append(connection_result)

        if "portfolios" in arguments:
            result["portfolios"] = []
            for portfolio in user_data.portfolios:
                portfolio_result = {
                    "uuid": portfolio.uuid,
                    "title": portfolio.title,
                    "content": portfolio.content
                }
                result["portfolios"].append(portfolio_result)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred"
        )
