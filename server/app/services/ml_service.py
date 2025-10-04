"""
ML SERVICE
==========
Handles machine learning model loading and inference.
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging

logger = logging.getLogger(__name__)

class MLService:
    """
    Machine Learning Service
    
    Why: Encapsulates all ML logic in one place
    What: Loads model, runs inference, returns predictions
    Without: Would need to duplicate model loading everywhere
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_name = os.getenv("MODEL_NAME", "distilbert-base-uncased")
        self.initialized = False
    
    async def initialize(self):
        """
        Initialize ML model and tokenizer
        
        Why: Load model once at startup, not on every request
        What: Downloads model from Hugging Face and loads into memory
        Without: 5-10 second delay on EVERY request
        """
        if self.initialized:
            logger.info("Model already initialized")
            return
        
        try:
            logger.info(f"📦 Loading model: {self.model_name}")
            
            # Determine device (GPU if available, else CPU)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"🔥 Using device: {self.device}")
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model
            logger.info("Loading model...")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name
            )
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            self.initialized = True
            logger.info("✅ Model initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize model: {e}")
            raise
    
    async def predict(self, text: str) -> dict:
        """
        Run inference on text
        
        Why: This is where the AI magic happens
        What: 
            1. Tokenizes text
            2. Runs through model
            3. Calculates probabilities
            4. Returns prediction + confidence
        Without: No ML predictions
        
        Args:
            text: The news text to analyze
            
        Returns:
            dict with 'prediction' (FAKE/REAL) and 'confidence' (0-1)
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run inference (no gradient calculation needed)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # Calculate probabilities
            probs = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get prediction (0=FAKE, 1=REAL)
            pred_class = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][pred_class].item()
            
            # Map to label
            label = "REAL" if pred_class == 1 else "FAKE"
            
            logger.info(f"ML Prediction: {label} (confidence: {confidence:.2%})")
            
            return {
                "prediction": label,
                "confidence": float(confidence),
                "probabilities": {
                    "FAKE": float(probs[0][0]),
                    "REAL": float(probs[0][1])
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

# Create singleton instance
ml_service = MLService()