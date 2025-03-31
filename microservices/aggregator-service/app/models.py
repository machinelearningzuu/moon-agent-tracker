from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class AggregationType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class AggregationStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Aggregation(Base):
    __tablename__ = "aggregations"

    aggregation_id = Column(String, primary_key=True, index=True)
    type = Column(Enum(AggregationType))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum(AggregationStatus), default=AggregationStatus.PENDING)
    created_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    results = relationship("AggregationResult", back_populates="aggregation")

class AggregationResult(Base):
    __tablename__ = "aggregation_results"

    result_id = Column(String, primary_key=True, index=True)
    aggregation_id = Column(String, ForeignKey("aggregations.aggregation_id"))
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    branch_id = Column(String, ForeignKey("branches.branch_id"))
    team_id = Column(String, ForeignKey("teams.team_id"))
    total_sales = Column(Numeric(10, 2))
    total_commission = Column(Numeric(10, 2))
    sales_count = Column(Numeric(10, 0))
    product_breakdown = Column(Text)  # JSON string for product-wise breakdown
    created_at = Column(DateTime)

    # Relationships
    aggregation = relationship("Aggregation", back_populates="results")
    agent = relationship("Agent")
    branch = relationship("Branch")
    team = relationship("Team") 