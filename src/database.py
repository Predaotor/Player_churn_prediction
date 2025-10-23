from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/churn_prediction")

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables (for development)
def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

# Drop all tables (for development/testing)
def drop_tables():
    """Drop all tables in the database"""
    Base.metadata.drop_all(bind=engine)
