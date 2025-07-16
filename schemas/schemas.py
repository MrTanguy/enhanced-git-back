from typing import Optional, Union
from pydantic import BaseModel

class PortfolioUpdateSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[Union[dict, list]] = None