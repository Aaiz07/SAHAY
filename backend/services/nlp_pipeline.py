"""
NLP pipeline: Translation → Classification → NER → Geocoding.
All heavy lifting is done via the Hugging Face Inference API so that
the backend has no mandatory GPU dependency.
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional, Tuple

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
GOOGLE_TRANSLATE_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")

HF_BASE = "https://api-inference.huggingface.co/models"
CLASSIFIER_MODEL = "facebook/bart-large-mnli"
NER_MODEL = "Jean-Baptiste/roberta-large-ner-english"

EMERGENCY_LABELS = ["medical emergency", "fire incident", "flood rescue", "building collapse", "traffic accident"]
SEVERITY_LABELS = ["critical high severity", "medium severity", "low severity"]

LABEL_MAP = {
    "medical emergency": "MEDICAL",
    "fire incident": "FIRE",
    "flood rescue": "FLOOD",
    "building collapse": "COLLAPSE",
    "traffic accident": "ACCIDENT",
}
SEVERITY_MAP = {
    "critical high severity": "HIGH",
    "medium severity": "MEDIUM",
    "low severity": "LOW",
}

# Simple geocoding lookup for common Indian locations
GEOCODE_DB: Dict[str, Tuple[float, float]] = {
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "whitefield": (12.9698, 77.7500),
    "electronic city": (12.8399, 77.6770),
    "koramangala": (12.9352, 77.6245),
    "indiranagar": (12.9784, 77.6408),
    "hyderabad": (17.3850, 78.4867),
    "hitech city": (17.4435, 78.3772),
    "secunderabad": (17.4399, 78.4983),
    "chennai": (13.0827, 80.2707),
    "velachery": (12.9815, 80.2180),
    "tambaram": (12.9249, 80.1000),
    "pune": (18.5204, 73.8567),
    "hinjewadi": (18.5912, 73.7389),
    "wakad": (18.6012, 73.7583),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "kolkata": (22.5726, 88.3639),
    "ahmedabad": (23.0225, 72.5714),
}

DEFAULT_COORDS = (12.9716, 77.5946)  # Default to Bengaluru


def _hf_headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}


def translate_to_english(text: str) -> str:
    """Translate text to English using Google Cloud Translation API.
    Falls back to original text on any error."""
    if not GOOGLE_TRANSLATE_KEY:
        logger.warning("GOOGLE_TRANSLATE_API_KEY not set – skipping translation")
        return text
    try:
        resp = httpx.post(
            "https://translation.googleapis.com/language/translate/v2",
            params={"key": GOOGLE_TRANSLATE_KEY},
            json={"q": text, "target": "en", "format": "text"},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["data"]["translations"][0]["translatedText"]
    except Exception as exc:
        logger.error("Translation failed: %s", exc)
        return text


def classify_emergency(text: str) -> Tuple[str, str]:
    """Zero-shot classify emergency type and severity.
    Returns (emergency_type, severity)."""
    if not HF_API_KEY:
        logger.warning("HUGGINGFACE_API_KEY not set – using heuristic classification")
        return _heuristic_classify(text)
    try:
        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": EMERGENCY_LABELS},
        }
        resp = httpx.post(
            f"{HF_BASE}/{CLASSIFIER_MODEL}",
            headers=_hf_headers(),
            json=payload,
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        top_label = data["labels"][0]
        emergency_type = LABEL_MAP.get(top_label, "MEDICAL")

        # Second pass for severity
        sev_payload = {
            "inputs": text,
            "parameters": {"candidate_labels": SEVERITY_LABELS},
        }
        sev_resp = httpx.post(
            f"{HF_BASE}/{CLASSIFIER_MODEL}",
            headers=_hf_headers(),
            json=sev_payload,
            timeout=30.0,
        )
        sev_resp.raise_for_status()
        sev_data = sev_resp.json()
        severity = SEVERITY_MAP.get(sev_data["labels"][0], "MEDIUM")
        return emergency_type, severity
    except Exception as exc:
        logger.error("HF classification failed: %s", exc)
        return _heuristic_classify(text)


def _heuristic_classify(text: str) -> Tuple[str, str]:
    """Simple keyword-based fallback classifier."""
    lower = text.lower()
    if any(k in lower for k in ("fire", "aag", "burning", "flames", "smoke")):
        etype = "FIRE"
    elif any(k in lower for k in ("flood", "water", "baarish", "drowning", "rescue")):
        etype = "FLOOD"
    elif any(k in lower for k in ("collapse", "building", "wall", "rubble", "debris")):
        etype = "COLLAPSE"
    elif any(k in lower for k in ("accident", "crash", "vehicle", "highway", "road")):
        etype = "ACCIDENT"
    else:
        etype = "MEDICAL"

    if any(k in lower for k in ("critical", "dead", "death", "trapped", "severe", "urgent", "immediately")):
        severity = "HIGH"
    elif any(k in lower for k in ("injured", "hurt", "serious", "hospital")):
        severity = "MEDIUM"
    else:
        severity = "LOW"
    return etype, severity


def extract_ner(text: str) -> Dict[str, Any]:
    """Run NER to extract location entities and estimate casualties."""
    locations: list[str] = []
    casualties = 0

    if HF_API_KEY:
        try:
            resp = httpx.post(
                f"{HF_BASE}/{NER_MODEL}",
                headers=_hf_headers(),
                json={"inputs": text},
                timeout=30.0,
            )
            resp.raise_for_status()
            entities = resp.json()
            for ent in entities:
                if isinstance(ent, dict) and ent.get("entity_group") in ("LOC", "GPE", "ORG"):
                    word = ent.get("word", "").strip()
                    if word:
                        locations.append(word)
        except Exception as exc:
            logger.error("NER failed: %s", exc)

    # Extract casualty counts with regex regardless.
    # Quantifiers are bounded (\d{1,4}) and require at least one whitespace (\s+)
    # to prevent polynomial backtracking (ReDoS) on adversarial input.
    numbers = re.findall(
        r"(\d{1,4})\s+(?:people|persons?|casualties|injured|dead|hurt|trapped)\b",
        text,
        re.I,
    )
    if numbers:
        casualties = sum(int(n) for n in numbers)

    # Keyword-based location fallback
    if not locations:
        for place in GEOCODE_DB:
            if place in text.lower():
                locations.append(place.title())

    return {"locations": locations, "casualties": casualties}


def geocode_location(location_name: str) -> Tuple[float, float]:
    """Convert a place name to (lat, lng). Uses local lookup then defaults."""
    key = location_name.lower().strip()
    for place, coords in GEOCODE_DB.items():
        if place in key or key in place:
            return coords
    return DEFAULT_COORDS


def run_pipeline(raw_text: str) -> Dict[str, Any]:
    """
    Full pipeline:
      1. Translate to English
      2. Classify emergency type + severity
      3. Extract NER (locations, casualties)
      4. Geocode
    Returns structured dict ready for DB insertion.
    """
    translated = translate_to_english(raw_text)
    emergency_type, severity = classify_emergency(translated)
    ner_result = extract_ner(translated)

    location_name = ner_result["locations"][0] if ner_result["locations"] else "Unknown"
    lat, lng = geocode_location(location_name)

    return {
        "translated_text": translated,
        "emergency_type": emergency_type,
        "severity": severity,
        "location": location_name,
        "lat": lat,
        "lng": lng,
        "casualties": ner_result["casualties"],
    }
