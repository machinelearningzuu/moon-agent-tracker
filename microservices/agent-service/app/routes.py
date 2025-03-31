from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from .database import get_db
from .models import Agent
from .schemas import Agent as AgentSchema

router = APIRouter()

@router.get("/", response_model=List[AgentSchema])
def get_all_agents(db: Session = Depends(get_db)):
    try:
        return db.query(Agent).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{agent_id}", response_model=AgentSchema)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    try:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/", response_model=AgentSchema)
def create_agent(agent: AgentSchema, db: Session = Depends(get_db)):
    try:
        db_agent = Agent(**agent.dict())
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return db_agent
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{agent_id}", response_model=AgentSchema)
def update_agent(agent_id: str, agent: AgentSchema, db: Session = Depends(get_db)):
    try:
        db_agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not db_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        for key, value in agent.dict().items():
            setattr(db_agent, key, value)
        
        db.commit()
        db.refresh(db_agent)
        return db_agent
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{agent_id}")
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    try:
        db_agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not db_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        db.delete(db_agent)
        db.commit()
        return {"message": "Agent deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
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