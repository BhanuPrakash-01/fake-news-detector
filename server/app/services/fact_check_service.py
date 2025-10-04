"""
FACT-CHECK SERVICE
==================
Queries external fact-checking APIs for claim verification.
"""

import os
import httpx
import logging
from typing import List

logger = logging.getLogger(__name__)

class FactCheckService:
    """
    Fact-Checking Service
    
    Why: Provide external, authoritative verification
    What: Queries Google Fact Check Tools API
    Without: Only relying on ML (less trustworthy)
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    async def check_claims(self, text: str) -> List[dict]:
        """
        Search for fact-checks related to the text
        
        Why: Get professional fact-checker verdicts
        What: 
            1. Extracts key claims from text
            2. Queries Google Fact Check API
            3. Parses and returns results
        Without: Missing critical external validation
        
        Args:
            text: The news text to fact-check
            
        Returns:
            List of fact-check results
        """
        
        # Check if API key is configured
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.warning("⚠️ Google Fact Check API key not configured")
            return []
        
        try:
            # Extract first 100 chars as query (simplified approach)
            # In production, you'd use NLP to extract key claims
            query = text[:100]
            
            logger.info(f"🔍 Querying Fact Check API for: {query[:50]}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "query": query,
                        "key": self.api_key,
                        "languageCode": "en"
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.warning(f"Fact Check API returned status {response.status_code}")
                    return []
                
                data = response.json()
                
                # Parse results
                fact_checks = []
                
                if "claims" in data:
                    for claim in data["claims"][:5]:  # Limit to 5 results
                        for review in claim.get("claimReview", []):
                            fact_checks.append({
                                "claim": claim.get("text", ""),
                                "claimant": claim.get("claimant", "Unknown"),
                                "rating": review.get("textualRating", "Unknown"),
                                "source": review.get("publisher", {}).get("name", "Unknown"),
                                "url": review.get("url", None)
                            })
                
                logger.info(f"✅ Found {len(fact_checks)} fact-check results")
                return fact_checks
                
        except httpx.TimeoutException:
            logger.warning("⏱️ Fact Check API timeout")
            return []
        except Exception as e:
            logger.error(f"❌ Fact check failed: {e}")
            return []

# Create singleton instance
fact_check_service = FactCheckService()