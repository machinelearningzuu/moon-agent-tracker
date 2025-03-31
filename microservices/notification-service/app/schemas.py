from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import Optional, Union, Dict, Any
from .models import NotificationType, NotificationStatus

class NotificationBase(BaseModel):
    notification_id: str
    recipient_id: str
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.PENDING

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    created_at: datetime
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }