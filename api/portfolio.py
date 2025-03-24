
from typing import Annotated
from fastapi import APIRouter, Depends

from repositories.PortfolioRepository import PortfolioRepository
from services.security.bearer import Bearer

portfolio_router = APIRouter()

@portfolio_router.get("/create")
async def create_portfolio(user_id: Annotated[int, Depends(Bearer().get_user_id)]):
    try:
        PortfolioRepository().create(user_id=user_id)
        return
    except:
        pass