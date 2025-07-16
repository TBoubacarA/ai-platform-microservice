import pytest
from app.core.similarity import SimilarityCalculator
from unittest.mock import patch

def test_cosine_similarity():
    calc = SimilarityCalculator()
    score = calc.cosine_sim("cat", "cat")
    assert score == pytest.approx(1.0, 0.01)
    
    score = calc.cosine_sim("artificial intelligence", "machine learning")
    assert 0.0 <= score <= 1.0

def test_jaccard_similarity():
    calc = SimilarityCalculator()
    # "cat dog" vs "dog mouse" = intersection {dog} / union {cat, dog, mouse} = 1/3
    assert calc.jaccard_sim("cat dog", "dog mouse") == pytest.approx(1.0/3.0, 0.01)
    assert calc.jaccard_sim("apple", "orange") == 0.0

@patch("app.core.llm_proxy.LLMClient.similarity")  
def test_llm_based_similarity(mock_similarity):
    calc = SimilarityCalculator()
    
    # Test valid response
    mock_similarity.return_value = 0.75
    score = calc.llm_based_sim("hello", "hi")
    assert score == 0.75
    
    # Test fallback to cosine when LLM fails
    mock_similarity.side_effect = Exception("LLM Error")
    score = calc.llm_based_sim("artificial intelligence", "machine learning")
    assert 0.0 <= score <= 1.0

@patch("app.core.llm_proxy.LLMClient.similarity")
def test_direct_llm_similarity(mock_similarity):
    calc = SimilarityCalculator()
    mock_similarity.return_value = 0.8
    score = calc.direct_llm_sim("future", "prediction")
    assert score == 0.8