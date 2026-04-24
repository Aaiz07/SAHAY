"""
Geospatial utilities – Haversine distance and priority scoring.
"""

import math
from typing import List, Dict, Optional

# Simulated emergency resources in major Indian cities
EMERGENCY_RESOURCES: List[Dict] = [
    {"id": "AMB-BLR-01", "type": "AMBULANCE", "city": "Bengaluru", "lat": 12.9716, "lng": 77.5946},
    {"id": "AMB-BLR-02", "type": "AMBULANCE", "city": "Bengaluru", "lat": 12.9352, "lng": 77.6245},
    {"id": "FIRE-BLR-01", "type": "FIRE_TRUCK", "city": "Bengaluru", "lat": 12.9784, "lng": 77.6408},
    {"id": "AMB-HYD-01", "type": "AMBULANCE", "city": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
    {"id": "FIRE-HYD-01", "type": "FIRE_TRUCK", "city": "Hyderabad", "lat": 17.4126, "lng": 78.4071},
    {"id": "AMB-CHN-01", "type": "AMBULANCE", "city": "Chennai",   "lat": 13.0827, "lng": 80.2707},
    {"id": "FIRE-CHN-01", "type": "FIRE_TRUCK", "city": "Chennai",   "lat": 13.0569, "lng": 80.2425},
    {"id": "AMB-PUN-01", "type": "AMBULANCE", "city": "Pune",      "lat": 18.5204, "lng": 73.8567},
    {"id": "FIRE-PUN-01", "type": "FIRE_TRUCK", "city": "Pune",      "lat": 18.5014, "lng": 73.8635},
    {"id": "AMB-MUM-01", "type": "AMBULANCE", "city": "Mumbai",    "lat": 19.0760, "lng": 72.8777},
]


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return the great-circle distance in kilometres between two points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_resource(incident_lat: float, incident_lng: float,
                          resource_type: Optional[str] = None) -> Optional[Dict]:
    """Return the closest resource (optionally filtered by type)."""
    candidates = EMERGENCY_RESOURCES
    if resource_type:
        candidates = [r for r in EMERGENCY_RESOURCES if r["type"] == resource_type]
    if not candidates:
        return None
    return min(candidates, key=lambda r: haversine_km(incident_lat, incident_lng, r["lat"], r["lng"]))


def calculate_priority_score(severity: str, casualties: int,
                              incident_lat: float, incident_lng: float) -> float:
    """
    Priority score in [0, 100].
    Higher = more urgent.  Formula accounts for severity, casualty count,
    and distance to nearest ambulance (closer resource → higher urgency weight).
    """
    severity_weight = {"HIGH": 60.0, "MEDIUM": 35.0, "LOW": 15.0}.get(severity.upper(), 20.0)
    casualty_weight = min(casualties * 5, 30.0)

    nearest = find_nearest_resource(incident_lat, incident_lng)
    if nearest:
        dist_km = haversine_km(incident_lat, incident_lng, nearest["lat"], nearest["lng"])
        # Closer distance means faster response → slightly higher urgency
        distance_weight = max(0.0, 10.0 - dist_km * 0.5)
    else:
        distance_weight = 0.0

    return round(min(severity_weight + casualty_weight + distance_weight, 100.0), 2)


def get_all_resources() -> List[Dict]:
    return EMERGENCY_RESOURCES
