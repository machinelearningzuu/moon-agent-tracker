from pydantic import BaseModel
from typing import List

class Agent(BaseModel):
    agent_id: str
    name: str
    email: str
    phone: str
    branch_id: str
    team_id: str
    products_allowed: str
    status: str