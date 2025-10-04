"""
SYNTHESIS SERVICE
=================
Combines ML predictions and fact-check results into final verdict.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

class SynthesisService:
    """
    Result Synthesis Service
    
    Why: Need intelligent logic to combine multiple signals
    What: Applies rules to determine final verdict
    Without: Conflicting results, unclear decisions
    """
    
    def synthesize(
        self,
        ml_prediction: str,
        ml_confidence: float,
        fact_checks: List[dict]
    ) -> dict:
        """
        Synthesize final verdict from ML and fact-checks
        
        Why: Combine multiple sources of truth intelligently
        What: Applies decision rules:
            1. If fact-checkers found it FALSE -> FAKE (highest priority)
            2. If fact-checkers found it TRUE -> REAL (high priority)
            3. If no fact-checks and ML high confidence -> Trust ML
            4. If conflicting signals -> UNCERTAIN
        Without: Can't handle disagreements between sources
        
        Args:
            ml_prediction: ML model prediction (FAKE/REAL)
            ml_confidence: ML confidence score (0-1)
            fact_checks: List of fact-check results
            
        Returns:
            dict with 'verdict', 'confidence', and 'reasoning'
        """
        
        logger.info("⚖️ Synthesizing results...")
        logger.info(f"   ML: {ml_prediction} ({ml_confidence:.2%})")
        logger.info(f"   Fact checks: {len(fact_checks)} results")
        
        # ====================================================================
        # RULE 1: Fact-checkers have highest priority
        # ====================================================================
        
        if fact_checks:
            # Count how many say false vs true
            false_ratings = ["false", "pants on fire", "mostly false"]
            true_ratings = ["true", "mostly true", "correct"]
            
            false_count = sum(
                1 for fc in fact_checks 
                if any(rating in fc['rating'].lower() for rating in false_ratings)
            )
            
            true_count = sum(
                1 for fc in fact_checks 
                if any(rating in fc['rating'].lower() for rating in true_ratings)
            )
            
            logger.info(f"   Fact-check breakdown: {false_count} FALSE, {true_count} TRUE")
            
            # If majority say false
            if false_count > true_count and false_count > 0:
                return {
                    "verdict": "FAKE",
                    "confidence": min(0.95, 0.7 + (false_count * 0.1)),
                    "reasoning": (
                        f"Professional fact-checkers found this claim to be false. "
                        f"{false_count} fact-checker(s) rated it as false or misleading."
                    )
                }
            
            # If majority say true
            if true_count > false_count and true_count > 0:
                return {
                    "verdict": "REAL",
                    "confidence": min(0.95, 0.7 + (true_count * 0.1)),
                    "reasoning": (
                        f"Professional fact-checkers verified this claim as true. "
                        f"{true_count} fact-checker(s) confirmed its accuracy."
                    )
                }
            
            # If mixed signals and ML is confident
            if false_count == true_count and ml_confidence > 0.8:
                return {
                    "verdict": ml_prediction,
                    "confidence": ml_confidence * 0.85,  # Slightly reduce confidence
                    "reasoning": (
                        f"Fact-checkers provided mixed signals. Our AI model predicts "
                        f"this is {ml_prediction} with {ml_confidence:.0%} confidence."
                    )
                }
            
            # If mixed signals and ML is not confident
            if false_count == true_count:
                return {
                    "verdict": "UNCERTAIN",
                    "confidence": 0.5,
                    "reasoning": (
                        "Fact-checkers provided conflicting assessments, and our AI "
                        "model is not highly confident. More investigation needed."
                    )
                }
        
        # ====================================================================
        # RULE 2: No fact-checks, rely on ML
        # ====================================================================
        
        if ml_confidence > 0.85:
            return {
                "verdict": ml_prediction,
                "confidence": ml_confidence,
                "reasoning": (
                    f"No fact-checks found. Our AI model predicts this is {ml_prediction} "
                    f"with high confidence ({ml_confidence:.0%})."
                )
            }
        
        if ml_confidence > 0.65:
            return {
                "verdict": ml_prediction,
                "confidence": ml_confidence,
                "reasoning": (
                    f"No fact-checks found. Our AI model suggests this is likely "
                    f"{ml_prediction} ({ml_confidence:.0%} confidence)."
                )
            }
        
        # ====================================================================
        # RULE 3: Low confidence everywhere
        # ====================================================================
        
        return {
            "verdict": "UNCERTAIN",
            "confidence": ml_confidence,
            "reasoning": (
                f"No definitive fact-checks found, and our AI model has moderate "
                f"confidence ({ml_confidence:.0%}). This claim requires more context "
                f"or investigation."
            )
        }

# Create singleton instance
synthesis_service = SynthesisService()