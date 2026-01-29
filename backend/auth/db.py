from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.tables import Base
import os

# Ensure directory exists
DB_DIR = "/app/data"
os.makedirs(DB_DIR, exist_ok=True)

# Database file path (not directory!)
DB_FILE = os.path.join(DB_DIR, "test.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)