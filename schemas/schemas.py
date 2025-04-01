from typing import Optional
from pydantic import BaseModel

class PortfolioUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None