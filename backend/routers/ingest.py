"""
/api/ingest router – accepts a raw distress signal, runs NLP pipeline,
persists to DB, and returns the enriched incident.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import Incident, get_db
from services.nlp_pipeline import run_pipeline
from services.geospatial import calculate_priority_score

router = APIRouter()


class IngestRequest(BaseModel):
    text: str


class IngestResponse(BaseModel):
    id: int
    text: str
    translated_text: str | None
    emergency_type: str | None
    severity: str | None
    location: str | None
    lat: float | None
    lng: float | None
    casualties: int
    timestamp: datetime
    priority_score: float


@router.post("/ingest", response_model=IngestResponse)
def ingest_signal(payload: IngestRequest, db: Session = Depends(get_db)):
    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="text field must not be empty")

    nlp = run_pipeline(payload.text)

    priority = calculate_priority_score(
        severity=nlp["severity"] or "LOW",
        casualties=nlp["casualties"],
        incident_lat=nlp["lat"],
        incident_lng=nlp["lng"],
    )

    incident = Incident(
        text=payload.text,
        translated_text=nlp["translated_text"],
        emergency_type=nlp["emergency_type"],
        severity=nlp["severity"],
        location=nlp["location"],
        lat=nlp["lat"],
        lng=nlp["lng"],
        casualties=nlp["casualties"],
        timestamp=datetime.utcnow(),
        priority_score=priority,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
