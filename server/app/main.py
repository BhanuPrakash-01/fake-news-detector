"""
FAKE NEWS DETECTOR - FASTAPI BACKEND
=====================================
Main application entry point for the FastAPI server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CREATE FASTAPI APPLICATION
# ============================================================================
# Why: This is the central application object that handles all HTTP requests
# What: Initializes FastAPI with metadata and configuration
# Without: No web server to receive requests

app = FastAPI(
    title="Fake News Detector API",
    description="API for detecting fake news using ML and fact-checking APIs",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc UI at /redoc
)

# ============================================================================
# CONFIGURE CORS
# ============================================================================
# Why: Allows frontend (different port/domain) to make requests to backend
# What: Adds CORS middleware with allowed origins
# Without: Browser blocks all requests from frontend (CORS policy error)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

logger.info(f"CORS enabled for origins: {FRONTEND_URL}")

# ============================================================================
# IMPORT ROUTERS
# ============================================================================
# Why: Keeps code organized by grouping related endpoints
# What: Imports route handlers from separate files
# Without: All routes in one file (messy and hard to maintain)

from app.routers import analyze, health

# Register routers
app.include_router(health.router, tags=["Health"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])

# ============================================================================
# ROOT ENDPOINT
# ============================================================================
# Why: Provides basic info when someone visits the root URL
# What: Returns a welcome message with API info
# Without: 404 error at root URL

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Fake News Detector API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ============================================================================
# STARTUP EVENT
# ============================================================================
# Why: Initialize resources when server starts (like loading the ML model)
# What: Loads ML model into memory once at startup
# Without: Model loaded on every request (extremely slow)

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("🚀 Starting Fake News Detector API...")
    logger.info(f"📝 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"🌐 Frontend URL: {FRONTEND_URL}")
    
    # Import here to trigger model loading
    from app.services.ml_service import ml_service
    
    try:
        # This will load the model into memory
        await ml_service.initialize()
        logger.info("✅ ML model loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to load ML model: {e}")
        logger.warning("⚠️ API will start but predictions will fail")

# ============================================================================
# SHUTDOWN EVENT
# ============================================================================
# Why: Clean up resources when server stops
# What: Closes connections, saves state, etc.
# Without: Resource leaks and potential data loss

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down Fake News Detector API...")
    # Add any cleanup code here (close DB connections, etc.)

# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================
# Why: Catch unexpected errors and return proper JSON responses
# What: Intercepts all unhandled exceptions
# Without: Server crashes or returns HTML error pages

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("ENVIRONMENT") == "development" else "An error occurred"
        }
    )

# ============================================================================
# RUN SERVER (for development)
# ============================================================================
# Why: Allows running the server directly with `python main.py`
# What: Starts uvicorn server programmatically
# Without: Must use command line to start server

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"🌟 Starting server at http://{host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )