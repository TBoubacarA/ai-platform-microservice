import os
from openai import OpenAI
from app.config import Config
import logging
import json

# Configuration du logging
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        try:
            # Nouvelle API OpenAI v1.x - pas d'arguments 'proxies' ou autres
            if Config.LLM_API_KEY:
                self.client = OpenAI(api_key=Config.LLM_API_KEY)
            else:
                self.client = None
                
            self.model = Config.LLM_MODEL
            self.max_tokens = Config.LLM_MAX_TOKENS
            logger.info("LLMClient initialized with model: %s", self.model)
        except Exception as e:
            logger.error("Error initializing LLMClient: %s", str(e))
            self.client = None
            self.model = "gpt-3.5-turbo"
            self.max_tokens = 150
    
    def generate(self, prompt: str) -> str:
        """Generate text from prompt using new OpenAI API"""
        if not self.client:
            error_msg = "LLM service not configured. Please set LLM_API_KEY in .env file."
            logger.warning(error_msg)
            return error_msg
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def similarity(self, text1: str, text2: str) -> float:
        """Direct similarity assessment using LLM with structured output"""
        prompt = f"""
        Compare these two texts and provide a similarity score between 0 and 1.
        
        Text 1: "{text1}"
        Text 2: "{text2}"
        
        Respond with a JSON object in this exact format:
        {{"similarity_score": 0.X, "reasoning": "brief explanation"}}
        
        The similarity_score must be a decimal number between 0.0 and 1.0.
        """
        
        try:
            response = self.generate(prompt)
            # Try to parse JSON response
            try:
                result = json.loads(response)
                if isinstance(result, dict):
                    score = float(result.get("similarity_score", 0.0))
                else:
                    score = float(result) if result else 0.0
                # Ensure score is within valid range
                return max(0.0, min(1.0, score))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                # Fallback: try to extract number from response
                import re
                numbers = re.findall(r'0\.\d+|1\.0+|0\.0+', response)
                if numbers:
                    try:
                        return float(numbers[0])
                    except ValueError:
                        return 0.0
                return 0.0
                
        except Exception as e:
            logger.error("Error in similarity assessment: %s", str(e))
            return 0.0
