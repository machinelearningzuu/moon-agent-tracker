from sqlalchemy import Column, String, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(String(50), primary_key=True, index=True)
    agent_id = Column(String(50))
    product_id = Column(String(50))
    sale_amount = Column(Numeric(10, 2))
    timestamp = Column(DateTime, default=datetime.now)
    branch_id = Column(String(50))
    team_id = Column(String(50))

class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100))
    category = Column(String(50))
    commission_percentage = Column(Numeric(5, 2))
    status = Column(String(20))