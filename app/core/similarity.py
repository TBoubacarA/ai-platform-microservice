import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
import logging
from app.core.llm_proxy import LLMClient

logger = logging.getLogger(__name__)

class SimilarityCalculator:
    def __init__(self):
        self.llm_client = LLMClient()
        # Amélioration du TF-IDF pour capturer plus de similarités
        self.tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # Unigrams et bigrams
            min_df=1,           # Minimum document frequency
            max_features=5000,  # Limite du vocabulaire
            stop_words='english'  # Supprime les mots vides
        )
    
    def cosine_sim(self, text1: str, text2: str) -> float:
        """Cosine similarity using TF-IDF - retourne un float Python"""
        try:
            if not text1.strip() or not text2.strip():
                return 0.0
            
            # Handle identical texts
            if text1.strip() == text2.strip():
                return 1.0
                
            vectors = self.tfidf_vectorizer.fit_transform([text1, text2])
            similarity_matrix = cosine_similarity(vectors[0:1], vectors[1:2])
            
            # Extraction et conversion explicite en float Python
            result = similarity_matrix[0][0]
            
            # S'assurer que c'est un float Python, pas numpy
            if isinstance(result, np.floating):
                return float(result)
            else:
                return float(result)
                
        except Exception as e:
            logger.error(f"Error in cosine similarity: {str(e)}")
            return 0.0
    
    def jaccard_sim(self, text1: str, text2: str) -> float:
        """Jaccard similarity coefficient - retourne un float Python"""
        try:
            words1 = set(word_tokenize(text1.lower()))
            words2 = set(word_tokenize(text2.lower()))
            intersection = words1 & words2
            union = words1 | words2
            
            if len(union) == 0:
                return 0.0
            
            # Calcul avec conversion explicite
            result = len(intersection) / len(union)
            
            # S'assurer que c'est un float Python
            return float(result)
            
        except Exception as e:
            logger.error(f"Error in jaccard similarity: {str(e)}")
            return 0.0
    
    def llm_based_sim(self, text1: str, text2: str) -> float:
        """LLM-enhanced similarity (fallback to cosine if LLM unavailable)"""
        try:
            # Essayer d'abord avec LLM
            if hasattr(self.llm_client, 'client') and self.llm_client.client:
                return self.direct_llm_sim(text1, text2)
            else:
                # Fallback vers cosine
                return self.cosine_sim(text1, text2)
        except Exception as e:
            logger.error(f"Error in llm_based similarity: {str(e)}")
            # Fallback vers cosine en cas d'erreur
            return self.cosine_sim(text1, text2)
    
    def direct_llm_sim(self, text1: str, text2: str) -> float:
        """Direct similarity assessment using LLM - retourne un float Python"""
        try:
            if not hasattr(self.llm_client, 'client') or not self.llm_client.client:
                logger.warning("LLM client not available, falling back to cosine")
                return self.cosine_sim(text1, text2)
            
            result = self.llm_client.similarity(text1, text2)
            
            # S'assurer que c'est un float Python dans la plage [0, 1]
            if isinstance(result, (np.floating, np.integer)):
                result = float(result)
            else:
                result = float(result) if result else 0.0
            
            # Clamp à [0, 1]
            return max(0.0, min(1.0, result))
            
        except Exception as e:
            logger.error(f"Error in direct LLM similarity: {str(e)}")
            # Fallback vers cosine
            return self.cosine_sim(text1, text2)