"""
HEALTH CHECK ROUTER
===================
Simple endpoint to verify server is running.
"""

from fastapi import APIRouter
from datetime import datetime
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Why: Used by monitoring tools and deployment platforms
    What: Returns server status and timestamp
    Without: No way to verify if server is alive
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }