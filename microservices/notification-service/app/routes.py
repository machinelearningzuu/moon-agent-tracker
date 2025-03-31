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

async def validate_agent(agent_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENT_SERVICE_URL}/agents/{agent_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Agent not found")
            return response.json()
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Agent service unavailable")

@router.post("/", response_model=NotificationSchema)
async def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    try:
        # Validate agent exists
        await validate_agent(notification.recipient_id)
        
        db_notification = Notification(
            **notification.dict(),
            created_at=datetime.now()
        )
        
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/{agent_id}", response_model=List[NotificationSchema])
async def get_agent_notifications(agent_id: str, db: Session = Depends(get_db)):
    try:
        # Validate agent exists
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
            
        return response_notifications
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sales/notify")
async def notify_sale(sale_data: dict, db: Session = Depends(get_db)):
    try:
        # Create notification for the agent
        notification = NotificationCreate(
            notification_id=f"sale_{sale_data['sale_id']}",
            recipient_id=sale_data['agent_id'],
            type=NotificationType.SALE,
            title="New Sale Recorded",
            message=f"Sale {sale_data['sale_id']} has been recorded successfully",
            status=NotificationStatus.PENDING
        )
        
        return await create_notification(notification, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{notification_id}/status")
async def update_notification_status(
    notification_id: str,
    status_update: StatusUpdate,  # Change this parameter
    db: Session = Depends(get_db)
):
    try:
        notification = db.query(Notification)\
            .filter(Notification.notification_id == notification_id)\
            .first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.status = status_update.status  # Update this line
        if status_update.status == NotificationStatus.SENT:  # Update this line
            notification.sent_at = datetime.now()
        
        db.commit()
        return {"message": "Notification status updated successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    return {"status": "healthy"}