"""
SAHAY: AI-Powered Crisis Triage & Resource Allocator
Main FastAPI Application Entry Point
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import routers after setup
from routers import incidents, ingest, resources

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for app startup and shutdown."""
    logger.info("🚀 SAHAY Server Starting...")
    yield
    logger.info("🛑 SAHAY Server Shutting Down...")

# Initialize FastAPI app
app = FastAPI(
    title="SAHAY - Crisis Triage API",
    description="AI-Enhanced Disaster Response Resource Allocator for Indian Municipalities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)

# Include routers
app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingest"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(resources.router, prefix="/api/resources", tags=["Resources"])

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API status check."""
    return {
        "status": "operational",
        "service": "SAHAY Crisis Triage System",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "healthy",
        "service": "SAHAY"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )