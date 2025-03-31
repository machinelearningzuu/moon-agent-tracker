from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
MYSQL_USER = os.getenv("MYSQL_USER", "2418250")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "cmm707")
MYSQL_SERVER = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_DB = os.getenv("MYSQL_DB", "moon agent tracker")

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}/{MYSQL_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 