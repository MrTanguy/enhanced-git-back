
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from repositories.PortfolioRepository import PortfolioRepository
from schemas.schemas import PortfolioUpdateSchema
from services.security.bearer import Bearer

portfolio_router = APIRouter()

@portfolio_router.get("/create")
async def create_portfolio(user_id: Annotated[int, Depends(Bearer().get_user_id)]):
    try:
        return PortfolioRepository().create(user_id=user_id)
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@portfolio_router.get("/{portfolio_ulid}")
async def get_portfolio_by_ulid(portfolio_ulid: str):
    try:
        # Appel de la méthode pour récupérer le portfolio par ULID
        portfolio = PortfolioRepository().get_by_ulid(portfolio_ulid)

        return {
            "title": portfolio.title,
            "description": portfolio.description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@portfolio_router.patch("/{portfolio_ulid}")
async def update_portfolio(user_id: Annotated[int, Depends(Bearer().get_user_id)], portfolio_ulid: str, update_data: PortfolioUpdateSchema):
    portfolio_repository = PortfolioRepository()

    portfolio = portfolio_repository.get_by_ulid(portfolio_ulid)

    if portfolio.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this resource")

    try:
        updated_portfolio = portfolio_repository.update(portfolio_ulid, update_data)
        return updated_portfolio
    except Exception as e:
        print(f"Error updating portfolio: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    