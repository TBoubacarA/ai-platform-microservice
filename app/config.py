import os
from dotenv import load_dotenv
from typing import List
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    # Service configuration
    PORT = int(os.getenv("PORT", 8003))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.7))
    DEFAULT_METRIC = os.getenv("DEFAULT_METRIC", "cosine")
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 1000))
    BLACKLIST = [word.strip() for word in os.getenv("BLACKLIST", "").split(",") if word.strip()]
    
    # LLM configuration (UPDATED for OpenAI v1.x)
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")  # Updated default model
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 150))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
    
    # Embedding configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 60))
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        if not cls.LLM_API_KEY:
            issues.append("LLM_API_KEY is not set - LLM features will be disabled")
        
        if cls.SIMILARITY_THRESHOLD < 0 or cls.SIMILARITY_THRESHOLD > 1:
            issues.append("SIMILARITY_THRESHOLD must be between 0 and 1")
        
        valid_metrics = ["cosine", "jaccard", "llm", "direct_llm"]
        if cls.DEFAULT_METRIC not in valid_metrics:
            issues.append(f"DEFAULT_METRIC must be one of: {valid_metrics}")
        
        if cls.MAX_INPUT_LENGTH < 1:
            issues.append("MAX_INPUT_LENGTH must be positive")
        
        if cls.LLM_MAX_TOKENS < 1:
            issues.append("LLM_MAX_TOKENS must be positive")
        
        return issues
    
    @classmethod
    def log_config(cls):
        """Log current configuration (without sensitive data)"""
        logger.info("=== AI Similarity Service Configuration ===")
        logger.info(f"PORT: {cls.PORT}")
        logger.info(f"SIMILARITY_THRESHOLD: {cls.SIMILARITY_THRESHOLD}")
        logger.info(f"DEFAULT_METRIC: {cls.DEFAULT_METRIC}")
        logger.info(f"MAX_INPUT_LENGTH: {cls.MAX_INPUT_LENGTH}")
        logger.info(f"LLM_MODEL: {cls.LLM_MODEL}")
        logger.info(f"LLM_MAX_TOKENS: {cls.LLM_MAX_TOKENS}")
        logger.info(f"EMBEDDING_MODEL: {cls.EMBEDDING_MODEL}")
        logger.info(f"API_KEY_CONFIGURED: {'Yes' if cls.LLM_API_KEY else 'No'}")
        logger.info(f"BLACKLIST_ITEMS: {len(cls.BLACKLIST)}")
        logger.info("=" * 45)

# Validate configuration on module load
config_issues = Config.validate()
if config_issues:
    logger.warning("Configuration validation issues:")
    for issue in config_issues:
        logger.warning(f"  ⚠️  {issue}")
else:
    logger.info("✅ Configuration validation passed")