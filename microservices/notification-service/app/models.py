from sqlalchemy import Column, String, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class NotificationType(enum.Enum):
    SALE = "SALE"
    COMMISSION = "COMMISSION"
    SYSTEM = "SYSTEM"
    ALERT = "ALERT"
    GENERAL = "GENERAL"

class NotificationStatus(enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String(50), primary_key=True, index=True)
    recipient_id = Column(String(50), index=True)
    type = Column(Enum(NotificationType))
    title = Column(String(200))
    message = Column(Text)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now)
    sent_at = Column(DateTime, nullable=True)