from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, confloat
from app.core.sanitization import Sanitizer
from app.core.similarity import SimilarityCalculator
from app.config import Config
import logging
import numpy as np

logger = logging.getLogger(__name__)

router = APIRouter()
sim_calculator = SimilarityCalculator()

# Modèle Pydantic avec validation étendue
class SimilarityRequest(BaseModel):
    prompt1: str
    prompt2: str
    metric: str = Config.DEFAULT_METRIC
    threshold: confloat(ge=0.0, le=1.0) = Config.SIMILARITY_THRESHOLD

def clean_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: clean_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(clean_numpy_types(item) for item in obj)
    else:
        return obj

@router.post("/similarity-check")
async def similarity_check(request: SimilarityRequest):
    try:
        logger.info("Received request: %s vs %s (%s)", 
                   request.prompt1[:20], request.prompt2[:20], request.metric)
        
        # Sanitize inputs
        try:
            p1_clean = Sanitizer.sanitize_input(request.prompt1)
            p2_clean = Sanitizer.sanitize_input(request.prompt2)
        except ValueError as e:
            logger.warning("Input sanitization failed: %s", str(e))
            raise HTTPException(status_code=400, detail=str(e))
        
        # Validate metric
        valid_metrics = ["cosine", "jaccard", "llm", "direct_llm"]
        if request.metric not in valid_metrics:
            error_msg = f"Invalid metric: {request.metric}. Valid options: {', '.join(valid_metrics)}"
            logger.warning(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Calculate similarity - avec gestion d'erreur robuste
        similarity_raw = 0.0
        
        try:
            if request.metric == "cosine":
                similarity_raw = sim_calculator.cosine_sim(p1_clean, p2_clean)
            elif request.metric == "jaccard":
                similarity_raw = sim_calculator.jaccard_sim(p1_clean, p2_clean)
            elif request.metric == "llm":
                similarity_raw = sim_calculator.llm_based_sim(p1_clean, p2_clean)
            elif request.metric == "direct_llm":
                similarity_raw = sim_calculator.direct_llm_sim(p1_clean, p2_clean)
            
        except Exception as e:
            logger.error("Similarity calculation failed: %s", str(e))
            # Valeur par défaut en cas d'erreur
            similarity_raw = 0.0
        
        # Nettoyer et convertir la similarité
        similarity = clean_numpy_types(similarity_raw)
        if not isinstance(similarity, (int, float)):
            similarity = float(similarity) if similarity else 0.0
        
        # Nettoyer le threshold
        threshold = clean_numpy_types(request.threshold)
        if not isinstance(threshold, (int, float)):
            threshold = float(threshold)
        
        # Calculer above_threshold et nettoyer
        above_threshold_raw = similarity > threshold
        above_threshold = clean_numpy_types(above_threshold_raw)
        if not isinstance(above_threshold, bool):
            above_threshold = bool(above_threshold)
        
        logger.info("Similarity calculated: %.4f using %s (threshold: %.2f, above: %s)", 
                   similarity, request.metric, threshold, above_threshold)
        
        # Generate LLM commentary ALWAYS (regardless of threshold)
        llm_response = None
        
        try:
            threshold_status = "above threshold (similar texts)" if above_threshold else "below threshold (dissimilar texts)"
            commentary_prompt = f"""
            Analyze and provide commentary on this text similarity comparison:
            
            Text 1: "{p1_clean}"
            Text 2: "{p2_clean}"
            
            Similarity Analysis:
            - Method used: {request.metric}
            - Similarity score: {similarity:.3f}
            - Threshold: {threshold}
            - Result: {threshold_status}
            
            Please provide a brief, insightful commentary explaining:
            - What makes these texts similar or different
            - Key semantic connections or differences
            - Why the similarity score makes sense for these texts
            
            Keep your response concise (2-3 sentences).
            """
            
            raw_response = sim_calculator.llm_client.generate(commentary_prompt)
            llm_response = Sanitizer.sanitize_output(raw_response) if raw_response else None
            logger.info("Generated LLM commentary")
            
        except Exception as e:
            llm_response = f"Error generating commentary: {str(e)}"
            logger.error("LLM commentary generation failed: %s", str(e))
        
        # Construire la réponse avec nettoyage complet
        response_data = {
            "similarity_score": round(float(similarity), 4),
            "similarity_metric": str(request.metric),
            "threshold": round(float(threshold), 4), 
            "above_threshold": bool(above_threshold),
            "llm_response": llm_response,
            "explanation": {
                "metric_description": {
                    "cosine": "TF-IDF cosine similarity - mathematical text vector comparison",
                    "jaccard": "Jaccard coefficient - token overlap ratio",
                    "llm": "LLM-enhanced similarity - combines mathematical and semantic analysis", 
                    "direct_llm": "Pure LLM assessment - semantic similarity evaluation"
                }.get(str(request.metric), "Unknown metric")
            }
        }
        
        # Nettoyage final de TOUTE la réponse
        cleaned_response = clean_numpy_types(response_data)
        
        return cleaned_response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.exception("Unexpected error in similarity check")
        # Réponse d'erreur nettoyée
        error_response = {
            "error": "Internal server error",
            "detail": str(e),
            "similarity_score": 0.0,
            "similarity_metric": str(request.metric) if hasattr(request, 'metric') else "unknown",
            "threshold": 0.5,
            "above_threshold": False,
            "llm_response": None
        }
        return clean_numpy_types(error_response)

@router.get("/health-detailed")
async def health_detailed():
    """Health check avec informations détaillées"""
    try:
        # Test de calcul simple
        test_calc = SimilarityCalculator()
        test_score = test_calc.cosine_sim("test", "test")
        test_score_clean = clean_numpy_types(test_score)
        
        health_data = {
            "status": "healthy",
            "port": int(Config.PORT),
            "similarity_test": float(test_score_clean),
            "llm_configured": bool(Config.LLM_API_KEY),
            "available_metrics": ["cosine", "jaccard", "llm", "direct_llm"]
        }
        
        return clean_numpy_types(health_data)
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e)
        }