import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found. Make sure it's set in your .env file."
    )

# -----------------------------
# SQLAlchemy Engine
# -----------------------------
engine = create_engine(DATABASE_URL)

# -----------------------------
# Session Factory
# -----------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -----------------------------
# Base class for models
# -----------------------------
Base = declarative_base()


# -----------------------------
# Dependency for FastAPI routes
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
