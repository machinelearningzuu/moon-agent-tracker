from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from typing import List
import httpx
import os
from datetime import datetime
import json
import logging

from .database import get_db
from .models import Notification, NotificationType, NotificationStatus
from .schemas import NotificationCreate, Notification as NotificationSchema

class StatusUpdate(BaseModel):
    status: NotificationStatus

router = APIRouter()
logger = logging.getLogger(__name__)

# Service URLs
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8000")
SALES_SERVICE_URL = os.getenv("SALES_SERVICE_URL", "http://sales-integration-service:8001")

# AGENT_SERVICE_URL = "http://localhost:8000"
# SALES_SERVICE_URL = "http://localhost:8001"

async def validate_agent(agent_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{AGENT_SERVICE_URL}/agents/{agent_id}"
            logger.info(f"About to request agent at: {url}")
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
        error_msg = f"Failed to connect to agent service at {url}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg)
    except httpx.HTTPError as e:
        error_msg = f"HTTP error while validating agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/", response_model=NotificationSchema)
async def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    try:
        # Validate agent exists
        logger.info(f"Creating notification for agent: {notification.recipient_id}")
        await validate_agent(notification.recipient_id)
        logger.info(f"Agent {notification.recipient_id} validated")
        
        db_notification = Notification(
            **notification.dict(),
            created_at=datetime.now()
        )
        
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        logger.info(f"Created notification {db_notification.notification_id} for agent {notification.recipient_id}")
        return db_notification
    
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status code and detail
        logger.error(f"HTTP error occurred: {e.detail}")
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        error_msg = f"Database error while creating notification for agent {notification.recipient_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error while creating notification: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/agent/{agent_id}", response_model=List[NotificationSchema])
async def get_agent_notifications(agent_id: str, db: Session = Depends(get_db)):
    try:
        # Validate agent exists
        logger.info(f"Getting notifications for agent: {agent_id}")
        await validate_agent(agent_id)
        
        notifications = db.query(Notification)\
            .filter(Notification.recipient_id == agent_id)\
            .order_by(Notification.created_at.desc())\
            .all()
        
        # Convert notifications to response format
        response_notifications = []
        for notif in notifications:
            notif_dict = {
                "notification_id": notif.notification_id,
                "recipient_id": notif.recipient_id,
                "type": notif.type,
                "title": notif.title,
                "message": notif.message,
                "status": notif.status,
                "created_at": notif.created_at,
                "sent_at": notif.sent_at
            }
            response_notifications.append(notif_dict)
            
        logger.info(f"Retrieved {len(notifications)} notifications for agent {agent_id}")
        return response_notifications
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status code and detail
        logger.error(f"HTTP error occurred: {e.detail}")
        raise e
    except SQLAlchemyError as e:
        error_msg = f"Database error while getting notifications for agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Error getting notifications for agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/sales/notify")
async def notify_sale(sale_data: dict, db: Session = Depends(get_db)):
    try:
        if 'sale_id' not in sale_data:
            error_msg = "Missing required field: sale_id in sale_data"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
            
        if 'agent_id' not in sale_data:
            error_msg = "Missing required field: agent_id in sale_data"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
            
        # Create notification for the agent
        notification = NotificationCreate(
            notification_id=f"sale_{sale_data['sale_id']}",
            recipient_id=sale_data['agent_id'],
            type=NotificationType.SALE,
            title="New Sale Recorded",
            message=f"Sale {sale_data['sale_id']} has been recorded successfully",
            status=NotificationStatus.PENDING
        )
        
        logger.info(f"Creating sale notification for agent {sale_data['agent_id']}, sale {sale_data['sale_id']}")
        return await create_notification(notification, db)
    except KeyError as e:
        error_msg = f"Missing required field in sale_data: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status code and detail
        raise e
    except Exception as e:
        error_msg = f"Error creating sale notification: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.put("/{notification_id}/status")
async def update_notification_status(
    notification_id: str,
    status_update: StatusUpdate,
    db: Session = Depends(get_db)
):
    try:
        notification = db.query(Notification)\
            .filter(Notification.notification_id == notification_id)\
            .first()
        
        if not notification:
            error_msg = f"Notification not found: {notification_id}"
            logger.warning(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        old_status = notification.status
        notification.status = status_update.status
        if status_update.status == NotificationStatus.SENT:
            notification.sent_at = datetime.now()
        
        db.commit()
        logger.info(f"Updated notification {notification_id} status from {old_status} to {status_update.status}")
        return {"message": f"Notification {notification_id} status updated from {old_status} to {status_update.status}"}
    except SQLAlchemyError as e:
        db.rollback()
        error_msg = f"Database error while updating notification {notification_id} status: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Error updating notification {notification_id} status: {str(e)}"
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