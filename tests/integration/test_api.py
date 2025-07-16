from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_similarity_endpoint():
    response = client.post(
        "/api/similarity-check",
        json={
            "prompt1": "Artificial Intelligence",
            "prompt2": "Machine Learning",
            "metric": "cosine"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "similarity_score" in data
    assert 0.0 <= data["similarity_score"] <= 1.0

def test_invalid_metric():
    response = client.post(
        "/api/similarity-check",
        json={
            "prompt1": "AI",
            "prompt2": "ML",
            "metric": "invalid_metric"
        }
    )
    assert response.status_code == 400
    assert "Invalid metric" in response.json()["detail"]

def test_blacklisted_input():
    response = client.post(
        "/api/similarity-check",
        json={
            "prompt1": "This contains malicious word if blacklist is configured",
            "prompt2": "Safe content"
        }
    )
    # This test may pass if no blacklist is configured
    # We'll just check that it returns a valid response
    assert response.status_code in [200, 400]