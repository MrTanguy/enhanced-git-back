"""Schemas used for request and response validation in the Enhanced Git API."""

from typing import Optional, Union
from pydantic import BaseModel


class PortfolioUpdateSchema(BaseModel):
    """
    Schema for updating a portfolio.

    Fields:
    - title: Optional title of the portfolio.
    - content: Optional content of the portfolio, can be a dict or a list.
    """
    title: Optional[str] = None
    content: Optional[Union[dict, list]] = None
