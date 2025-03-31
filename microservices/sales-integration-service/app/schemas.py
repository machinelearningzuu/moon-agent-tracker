from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class SaleBase(BaseModel):
    sale_id: str
    agent_id: str
    product_id: str
    sale_amount: Decimal
    branch_id: str
    team_id: str

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    timestamp: datetime

    class Config:
        from_attributes = True