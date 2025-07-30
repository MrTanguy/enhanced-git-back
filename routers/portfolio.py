from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from repositories.portfolio_repository import PortfolioRepository
from schemas.schemas import PortfolioUpdateSchema
from services.security.bearer import Bearer

portfolio_router = APIRouter()


@portfolio_router.get("/create")
async def create_portfolio(user_id: Annotated[int, Depends(Bearer().get_user_id)]):
    """
    Create a new portfolio for the given user.

    :param user_id: ID of the authenticated user
    :return: The created portfolio
    """
    try:
        return PortfolioRepository().create(user_id=user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc


@portfolio_router.get("/{portfolio_uuid}")
async def get_portfolio_by_uuid(portfolio_uuid: str):
    """
    Retrieve a portfolio by its UUID.

    :param portfolio_uuid: UUID of the portfolio
    :return: The portfolio object
    """
    try:
        return PortfolioRepository().get_by_uuid(portfolio_uuid)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc


@portfolio_router.patch("/{portfolio_uuid}")
async def update_portfolio(
    user_id: Annotated[int, Depends(Bearer().get_user_id)],
    portfolio_uuid: str,
    update_data: PortfolioUpdateSchema
):
    """
    Update a portfolio by UUID if the user is the owner.

    :param user_id: ID of the authenticated user
    :param portfolio_uuid: UUID of the portfolio to update
    :param update_data: New data for the portfolio
    :return: The updated portfolio
    """
    portfolio_repository = PortfolioRepository()
    portfolio = portfolio_repository.get_by_uuid(portfolio_uuid)

    if portfolio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this resource"
        )

    try:
        return portfolio_repository.update(portfolio_uuid, update_data)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc


@portfolio_router.delete("/{portfolio_uuid}")
async def delete_portfolio(
    user_id: Annotated[int, Depends(Bearer().get_user_id)],
    portfolio_uuid: str
):
    """
    Delete a portfolio by UUID if the user is the owner.

    :param user_id: ID of the authenticated user
    :param portfolio_uuid: UUID of the portfolio to delete
    """

    portfolio_repository = PortfolioRepository()
    portfolio = portfolio_repository.get_by_uuid(portfolio_uuid)


    if portfolio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this resource"
        )

    try:
        portfolio_repository.delete(uuid=portfolio_uuid)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc
