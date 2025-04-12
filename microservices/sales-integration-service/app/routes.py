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

# AGENT_SERVICE_URL = "http://localhost:8000"
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8000")

async def validate_agent(agent_id: str):
    try:
        logger.info(f"Validating agent: {agent_id}")
        logger.info(f"Agent service URL: {AGENT_SERVICE_URL}")
        url = f"{AGENT_SERVICE_URL}/agents/{agent_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            logger.info(f"Agent validation response status: {response.status_code}")
            
            if response.status_code == 404:
                error_msg = f"Agent not found: {agent_id}"
                logger.warning(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)
                
            if response.status_code != 200:
                error_msg = f"Unexpected response from agent service: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise HTTPException(status_code=response.status_code, detail=error_msg)
                
            logger.info(f"Agent {agent_id} validated successfully")
            return response.json()
    except httpx.ConnectError as e:
        error_msg = f"Connection error: Could not connect to agent service at {url}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=503,
            detail=error_msg
        )
    except httpx.HTTPError as e:
        error_msg = f"HTTP error while validating agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

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
            error_msg = f"Product {sale.product_id} not allowed for agent {sale.agent_id}. Allowed products: {products_allowed}"
            logger.warning(error_msg)
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )

        # Verify branch and team match the agent's data
        if sale.branch_id != agent_data.get('branch_id'):
            error_msg = f"Branch mismatch: Sale branch {sale.branch_id} != Agent branch {agent_data.get('branch_id')}"
            logger.warning(error_msg)
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )

        if sale.team_id != agent_data.get('team_id'):
            error_msg = f"Team mismatch: Sale team {sale.team_id} != Agent team {agent_data.get('team_id')}"
            logger.warning(error_msg)
            raise HTTPException(
                status_code=400,
                detail=error_msg
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
        
        logger.info(f"Sale created successfully: {db_sale.sale_id} for agent {db_sale.agent_id}")
        return db_sale
        
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status code and detail
        logger.error(f"HTTP error occurred: {e.detail}")
        raise e
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating sale: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while creating sale: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while creating sale: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/agent/{agent_id}", response_model=List[SaleSchema])
async def get_sales_by_agent(agent_id: str, db: Session = Depends(get_db)):
    try:
        # Log the received agent_id
        logger.info(f"Received request for sales by agent: {agent_id}")
    
        # Validate agent exists
        agent_data = await validate_agent(agent_id)
        logger.info(f"Agent validated: {agent_data}")
        
        sales = db.query(Sale).filter(Sale.agent_id == agent_id).all()
        logger.info(f"Found {len(sales)} sales for agent {agent_id}")
        return sales
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status code and detail
        logger.error(f"HTTP error occurred: {e.detail}")
        raise e
    except SQLAlchemyError as e:
        error_msg = f"Database error while retrieving sales for agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error while retrieving sales for agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/health")
def health_check():
    try:
        return {
            "status": "healthy",
            "database": "connected"
        }
    except SQLAlchemyError as e:
        error_msg = f"Database health check failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=503,
            detail=error_msg
        )   
