import re
import html
from app.config import Config

class Sanitizer:
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        # Check length
        if len(text) > Config.MAX_INPUT_LENGTH:
            raise ValueError(f"Input exceeds maximum length of {Config.MAX_INPUT_LENGTH} characters")
        
        # Remove HTML tags
        cleaned = re.sub(r'<[^>]*>', '', text)
        
        # Escape special characters
        cleaned = html.escape(cleaned)
        
        # Check for blacklisted words
        lower_text = cleaned.lower()
        for forbidden in Config.BLACKLIST:
            if forbidden and forbidden in lower_text:
                raise ValueError(f"Forbidden content detected: {forbidden}")
                
        return cleaned.strip()
    
    @staticmethod
    def sanitize_output(text: str) -> str:
        """Sanitize LLM output"""
        # Basic cleaning
        cleaned = re.sub(r'[\x00-\x1F\x7F]', '', text)  # Remove control characters
        
        # Truncate to safe length
        max_length = Config.MAX_INPUT_LENGTH * 2
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "... [TRUNCATED]"
            
        return cleaned