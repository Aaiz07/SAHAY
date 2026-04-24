"""
SQLAlchemy database models and session management for SAHAY.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sahay_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=True)
    emergency_type = Column(String(50), nullable=True)   # FIRE / MEDICAL / FLOOD / COLLAPSE / ACCIDENT
    severity = Column(String(20), nullable=True)         # HIGH / MEDIUM / LOW
    location = Column(String(255), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    casualties = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    priority_score = Column(Float, default=0.0)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
