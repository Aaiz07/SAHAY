"""
SAHAY – FastAPI application entry point.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models.database import create_tables
from routers import ingest, incidents

load_dotenv()

app = FastAPI(
    title="SAHAY – Disaster Response Resource Allocator",
    description="AI-powered crisis triage engine for Indian municipalities",
    version="1.0.0",
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "SAHAY API"}
