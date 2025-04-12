from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List
import logging

from .database import get_db
from .models import Agent
from .schemas import Agent as AgentSchema

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[AgentSchema])
def get_all_agents(db: Session = Depends(get_db)):
    try:
        agents = db.query(Agent).all()
        logger.info(f"Retrieved {len(agents)} agents")
        return agents
    except SQLAlchemyError as e:
        error_msg = f"Database error when retrieving all agents: {str(e)}"
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
        error_msg = f"Health check failed - database connection error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=503,
            detail=error_msg
        )

@router.get("/{agent_id}", response_model=AgentSchema)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    try:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            error_msg = f"Agent not found: {agent_id}"
            logger.warning(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        logger.info(f"Retrieved agent: {agent_id}")
        return agent
    except SQLAlchemyError as e:
        error_msg = f"Database error when retrieving agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/", response_model=AgentSchema)
def create_agent(agent: AgentSchema, db: Session = Depends(get_db)):
    try:
        # Check if agent already exists
        existing_agent = db.query(Agent).filter(Agent.agent_id == agent.agent_id).first()
        if existing_agent:
            error_msg = f"Agent already exists with ID: {agent.agent_id}"
            logger.warning(error_msg)
            raise HTTPException(status_code=409, detail=error_msg)
            
        db_agent = Agent(**agent.dict())
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        logger.info(f"Created new agent: {agent.agent_id}")
        return db_agent
    except SQLAlchemyError as e:
        db.rollback()
        error_msg = f"Database error when creating agent {agent.agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.put("/{agent_id}", response_model=AgentSchema)
def update_agent(agent_id: str, agent: AgentSchema, db: Session = Depends(get_db)):
    try:
        db_agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not db_agent:
            error_msg = f"Agent not found: {agent_id}"
            logger.warning(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        for key, value in agent.dict().items():
            setattr(db_agent, key, value)
        
        db.commit()
        db.refresh(db_agent)
        logger.info(f"Updated agent: {agent_id}")
        return db_agent
    except SQLAlchemyError as e:
        db.rollback()
        error_msg = f"Database error when updating agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.delete("/{agent_id}")
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    try:
        db_agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not db_agent:
            error_msg = f"Agent not found: {agent_id}"
            logger.warning(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        db.delete(db_agent)
        db.commit()
        logger.info(f"Deleted agent: {agent_id}")
        return {"message": f"Agent {agent_id} deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        error_msg = f"Database error when deleting agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)