"""
seed_data.py – Populates the database with 5 realistic mock distress signals
covering diverse Indian cities and emergency types.
Run: python seed_data.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from models.database import SessionLocal, Incident, create_tables
from services.nlp_pipeline import run_pipeline
from services.geospatial import calculate_priority_score

MOCK_SIGNALS = [
    # 1. Medical emergency – Bengaluru tech park (English)
    "URGENT: Multiple employees collapsed at Whitefield Tech Park, Bengaluru. "
    "Suspected gas leak, at least 8 people unconscious. Need ambulances immediately!",

    # 2. Fire incident – Hyderabad warehouse (Hindi)
    "हैदराबाद के हाईटेक सिटी गोदाम में भीषण आग लग गई है। "
    "करीब 20 मजदूर फंसे हुए हैं। कृपया दमकल गाड़ी तुरंत भेजें।",

    # 3. Flood / water rescue – Chennai flood-prone area (Tamil)
    "சென்னை வேளச்சேரியில் மிகப்பெரிய வெள்ளம். "
    "குழந்தைகள் உட்பட 15 பேர் மாடியில் சிக்கியுள்ளனர். "
    "படகு மீட்பு குழு அனுப்புங்கள்!",

    # 4. Building collapse – Pune construction site (English)
    "Building under construction collapsed near Wakad, Pune. "
    "Approximately 12 workers trapped under debris. Rescue teams needed urgently.",

    # 5. Traffic accident – Bangalore highway (English + Hindi mix)
    "Serious accident on Bengaluru–Mysuru highway near Electronic City. "
    "3 vehicles involved, 5 injured. एंबुलेंस और क्रेन की जरूरत है।",
]


def seed():
    create_tables()
    db = SessionLocal()
    try:
        existing = db.query(Incident).count()
        if existing > 0:
            print(f"Database already has {existing} incidents. Skipping seed.")
            return

        print("Seeding database with mock distress signals …")
        for i, raw_text in enumerate(MOCK_SIGNALS, start=1):
            print(f"  [{i}/{len(MOCK_SIGNALS)}] Processing signal …")
            nlp = run_pipeline(raw_text)
            priority = calculate_priority_score(
                severity=nlp["severity"] or "LOW",
                casualties=nlp["casualties"],
                incident_lat=nlp["lat"],
                incident_lng=nlp["lng"],
            )
            incident = Incident(
                text=raw_text,
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
        print("✅ Seeded 5 incidents successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
