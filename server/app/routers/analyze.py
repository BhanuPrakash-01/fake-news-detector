"""
ANALYSIS ROUTER
===============
Main endpoint for fake news detection.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================
# Why: Define structure of incoming/outgoing data
# What: Pydantic models for validation and documentation
# Without: No validation, unclear API contract

class AnalyzeRequest(BaseModel):
    """Request model for text analysis"""
    text: str = Field(
        ..., 
        min_length=10, 
        max_length=10000,
        description="The news text to analyze (10-10000 characters)"
    )
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        """Ensure text is not just whitespace"""
        if not v.strip():
            raise ValueError('Text cannot be empty or only whitespace')
        return v.strip()

class FactCheckResult(BaseModel):
    """Fact check result from external API"""
    claim: str
    claimant: Optional[str] = None
    rating: str
    source: str
    url: Optional[str] = None

class AnalyzeResponse(BaseModel):
    """Response model for analysis results"""
    verdict: str = Field(..., description="FAKE or REAL")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    ml_prediction: str = Field(..., description="ML model prediction")
    ml_confidence: float = Field(..., ge=0, le=1, description="ML confidence")
    fact_checks: List[FactCheckResult] = Field(default_factory=list)
    reasoning: str = Field(..., description="Explanation of the verdict")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")

# ============================================================================
# ANALYZE ENDPOINT
# ============================================================================

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text for fake news detection
    
    Why: This is the main functionality of our entire application
    What: 
        1. Receives text from frontend
        2. Runs ML model inference
        3. Queries fact-checking APIs
        4. Synthesizes results
        5. Returns verdict with confidence
    Without: The entire app is useless
    
    Args:
        request: AnalyzeRequest containing text to analyze
        
    Returns:
        AnalyzeResponse with verdict, confidence, and supporting evidence
        
    Raises:
        HTTPException: If analysis fails
    """
    import time
    start_time = time.time()
    
    logger.info(f"📥 Received analysis request (text length: {len(request.text)} chars)")
    
    try:
        # Import services
        from app.services.ml_service import ml_service
        from app.services.fact_check_service import fact_check_service
        from app.services.synthesis_service import synthesis_service
        
        # ====================================================================
        # STEP 1: ML MODEL PREDICTION
        # ====================================================================
        # Why: Get initial prediction from our trained model
        # What: Runs inference on the text
        # Without: No AI-powered analysis
        
        logger.info("🤖 Running ML model inference...")
        ml_result = await ml_service.predict(request.text)
        
        logger.info(f"🤖 ML Prediction: {ml_result['prediction']} "
                   f"(confidence: {ml_result['confidence']:.2%})")
        
        # ====================================================================
        # STEP 2: FACT-CHECKING API QUERIES
        # ====================================================================
        # Why: Verify claims against authoritative sources
        # What: Queries Google Fact Check API
        # Without: Only relying on ML (less robust)
        
        logger.info("🔍 Querying fact-check APIs...")
        fact_checks = await fact_check_service.check_claims(request.text)
        
        logger.info(f"🔍 Found {len(fact_checks)} fact-check results")
        
        # ====================================================================
        # STEP 3: SYNTHESIZE RESULTS
        # ====================================================================
        # Why: Combine ML + fact-checks into final verdict
        # What: Applies business logic to determine final answer
        # Without: Conflicting information, unclear verdict
        
        logger.info("⚖️ Synthesizing final verdict...")
        final_verdict = synthesis_service.synthesize(
            ml_prediction=ml_result['prediction'],
            ml_confidence=ml_result['confidence'],
            fact_checks=fact_checks
        )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Analysis complete: {final_verdict['verdict']} "
                   f"({processing_time:.0f}ms)")
        
        # ====================================================================
        # STEP 4: FORMAT AND RETURN RESPONSE
        # ====================================================================
        
        return AnalyzeResponse(
            verdict=final_verdict['verdict'],
            confidence=final_verdict['confidence'],
            ml_prediction=ml_result['prediction'],
            ml_confidence=ml_result['confidence'],
            fact_checks=fact_checks,
            reasoning=final_verdict['reasoning'],
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
