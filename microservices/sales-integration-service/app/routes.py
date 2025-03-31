from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import httpx, logging, os
from datetime import datetime

from .database import get_db
from .models import Sale, Product
from .schemas import Sale as SaleSchema, SaleCreate

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AGENT_SERVICE_URL = "http://localhost:8000/agents"
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8000")

async def validate_agent(agent_id: str):
    try:
        logger.info(f"Validating agent: {agent_id}")
        logger.info(f"Agent service URL: {AGENT_SERVICE_URL}")
        async with httpx.AsyncClient() as client:
            # Fix the endpoints by adding /agents
            all_agents = await client.get(f"{AGENT_SERVICE_URL}/agents/")
            logger.info(f"All agents response status: {all_agents.status_code}")
            if all_agents.status_code == 200:
                logger.info(f"Available agents: {all_agents.json()}")
            
            # Fix the specific agent endpoint
            response = await client.get(f"{AGENT_SERVICE_URL}/agents/{agent_id}")
            logger.info(f"Specific agent response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Agent not found")
            return response.json()
    except httpx.ConnectError as e:
        logger.error(f"Connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Could not connect to agent service"
        )

@router.post("/", response_model=SaleSchema)
async def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to create sale: {sale.dict()}")
        
        # Validate agent exists and get agent details
        agent_data = await validate_agent(sale.agent_id)
        logger.info(f"Agent validated: {agent_data}")
        
        # Check if product is allowed for this agent
        products_allowed = eval(agent_data.get('products_allowed', '[]'))
        logger.info(f"Products allowed for agent: {products_allowed}")
        
        if sale.product_id not in products_allowed:
            logger.warning(f"Product {sale.product_id} not allowed for agent {sale.agent_id}")
            raise HTTPException(
                status_code=400,
                detail=f"Agent {sale.agent_id} is not authorized to sell product {sale.product_id}"
            )

        # Verify branch and team match the agent's data
        if sale.branch_id != agent_data.get('branch_id'):
            logger.warning(f"Branch mismatch: Sale branch {sale.branch_id} != Agent branch {agent_data.get('branch_id')}")
            raise HTTPException(
                status_code=400,
                detail="Branch ID does not match agent's branch"
            )

        if sale.team_id != agent_data.get('team_id'):
            logger.warning(f"Team mismatch: Sale team {sale.team_id} != Agent team {agent_data.get('team_id')}")
            raise HTTPException(
                status_code=400,
                detail="Team ID does not match agent's team"
            )

        # Create sale record
        db_sale = Sale(
            sale_id=sale.sale_id,
            agent_id=sale.agent_id,
            product_id=sale.product_id,
            sale_amount=sale.sale_amount,
            timestamp=datetime.now(),
            branch_id=sale.branch_id,
            team_id=sale.team_id
        )
        
        logger.info(f"Creating sale record: {db_sale.__dict__}")
        
        db.add(db_sale)
        db.commit()
        db.refresh(db_sale)
        
        logger.info(f"Sale created successfully: {db_sale.__dict__}")
        return db_sale
        
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating sale: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while creating sale: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/{agent_id}", response_model=List[SaleSchema])
async def get_sales_by_agent(agent_id: str, db: Session = Depends(get_db)):
    try:
        # Log the received agent_id
        logger.info(f"Received request for agent_id: {agent_id}")
        
        # Validate agent exists
        agent_data = await validate_agent(agent_id)
        logger.info(f"Agent validated: {agent_data}")
        
        sales = db.query(Sale).filter(Sale.agent_id == agent_id).all()
        logger.info(f"Found {len(sales)} sales for agent")
        return sales
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/health")
def health_check():
    try:
        return {
            "status": "healthy",
            "database": "connected"
        }
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable - database connection failed"
        )
