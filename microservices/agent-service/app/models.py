from sqlalchemy import Column, String, Text, Table, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    branch_id = Column(String, ForeignKey("branches.branch_id"))
    team_id = Column(String, ForeignKey("teams.team_id"))
    products_allowed = Column(Text)  # Store as comma-separated string or use JSONB if PostgreSQL
    status = Column(String)

    # Relationships
    branch = relationship("Branch", back_populates="agents")
    team = relationship("Team", back_populates="agents")
    sales = relationship("Sale", back_populates="agent")

class Branch(Base):
    __tablename__ = "branches"

    branch_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)

    # Relationships
    agents = relationship("Agent", back_populates="branch")
    teams = relationship("Team", back_populates="branch")
    sales = relationship("Sale", back_populates="branch")

class Team(Base):
    __tablename__ = "teams"

    team_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    branch_id = Column(String, ForeignKey("branches.branch_id"))

    # Relationships
    branch = relationship("Branch", back_populates="teams")
    agents = relationship("Agent", back_populates="team")
    sales = relationship("Sale", back_populates="team")

class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    branch_id = Column(String, ForeignKey("branches.branch_id"))
    team_id = Column(String, ForeignKey("teams.team_id"))

    # Relationships
    agent = relationship("Agent", back_populates="sales")
    branch = relationship("Branch", back_populates="sales")
    team = relationship("Team", back_populates="sales")