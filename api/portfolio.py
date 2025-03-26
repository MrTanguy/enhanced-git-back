
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from repositories.PortfolioRepository import PortfolioRepository
from services.security.bearer import Bearer

portfolio_router = APIRouter()

@portfolio_router.get("/create")
async def create_portfolio(user_id: Annotated[int, Depends(Bearer().get_user_id)]):
    try:
        return PortfolioRepository().create(user_id=user_id)
    except:
        pass

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
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")