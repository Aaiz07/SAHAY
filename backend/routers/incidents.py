"""
/api/incidents router – returns all incidents ordered by priority score (desc).
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import Incident, get_db
from services.geospatial import find_nearest_resource

router = APIRouter()


class ResourceInfo(BaseModel):
    id: str
    type: str
    city: str
    lat: float
    lng: float
    distance_km: float | None = None


class IncidentResponse(BaseModel):
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
    nearest_resource: ResourceInfo | None = None

    class Config:
        from_attributes = True


@router.get("/incidents", response_model=List[IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.priority_score.desc()).all()
    result = []
    for inc in incidents:
        resource = None
        if inc.lat and inc.lng:
            r = find_nearest_resource(inc.lat, inc.lng)
            if r:
                from services.geospatial import haversine_km
                dist = haversine_km(inc.lat, inc.lng, r["lat"], r["lng"])
                resource = ResourceInfo(
                    id=r["id"],
                    type=r["type"],
                    city=r["city"],
                    lat=r["lat"],
                    lng=r["lng"],
                    distance_km=round(dist, 2),
                )
        result.append(
            IncidentResponse(
                id=inc.id,
                text=inc.text,
                translated_text=inc.translated_text,
                emergency_type=inc.emergency_type,
                severity=inc.severity,
                location=inc.location,
                lat=inc.lat,
                lng=inc.lng,
                casualties=inc.casualties,
                timestamp=inc.timestamp,
                priority_score=inc.priority_score,
                nearest_resource=resource,
            )
        )
    return result
