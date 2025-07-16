from locust import HttpUser, task, between
import random
import json

class SimilarityServiceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup executed when user starts"""
        self.test_prompts = [
            ("Artificial Intelligence", "Machine Learning"),
            ("Natural Language Processing", "Text Analysis"),
            ("Deep Learning", "Neural Networks"),
            ("Data Science", "Analytics"),
            ("Computer Vision", "Image Recognition"),
            ("Robotics", "Automation"),
            ("Cloud Computing", "Distributed Systems"),
            ("Cybersecurity", "Information Security")
        ]
    
    @task(4)
    def test_cosine_similarity(self):
        """Test cosine similarity - most common use case"""
        prompt1, prompt2 = random.choice(self.test_prompts)
        payload = {
            "prompt1": f"{prompt1} example {random.randint(1,1000)}",
            "prompt2": f"{prompt2} sample {random.randint(1,1000)}",
            "metric": "cosine",
            "threshold": random.choice([0.5, 0.7, 0.8])
        }
        
        with self.client.post("/api/similarity-check", 
                             json=payload, 
                             catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "similarity_score" in data:
                        response.success()
                    else:
                        response.failure("Missing similarity_score in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_jaccard_similarity(self):
        """Test Jaccard similarity"""
        prompt1, prompt2 = random.choice(self.test_prompts)
        payload = {
            "prompt1": prompt1,
            "prompt2": prompt2,
            "metric": "jaccard"
        }
        
        with self.client.post("/api/similarity-check", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Jaccard test failed: {response.status_code}")
    
    @task(1)
    def test_llm_similarity(self):
        """Test LLM-based similarity"""
        prompt1, prompt2 = random.choice(self.test_prompts)
        payload = {
            "prompt1": prompt1,
            "prompt2": prompt2,
            "metric": "llm",
            "threshold": 0.6
        }
        self.client.post("/api/similarity-check", json=payload)
    
    @task(1)
    def test_health_endpoint(self):
        """Health check"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Health check failed")
    
    @task(1)
    def test_home_endpoint(self):
        """Test home page"""
        self.client.get("/")

class HighLoadUser(HttpUser):
    """Simulates high-load scenario with rapid requests"""
    wait_time = between(0.1, 0.5)
    
    @task
    def rapid_cosine_requests(self):
        """Rapid fire cosine similarity requests"""
        payload = {
            "prompt1": f"quick test {random.randint(1,10000)}",
            "prompt2": f"fast test {random.randint(1,10000)}",
            "metric": "cosine"
        }
        self.client.post("/api/similarity-check", json=payload)

class ErrorTestUser(HttpUser):
    """Tests error handling and edge cases"""
    wait_time = between(2, 5)
    
    @task
    def test_invalid_metric(self):
        """Test invalid similarity metric"""
        payload = {
            "prompt1": "test prompt",
            "prompt2": "another test",
            "metric": "invalid_metric"
        }
        
        with self.client.post("/api/similarity-check", json=payload, catch_response=True) as response:
            if response.status_code == 400:
                response.success()  # We expect a 400 error
            else:
                response.failure(f"Expected 400, got {response.status_code}")
    
    @task
    def test_empty_prompts(self):
        """Test empty prompts"""
        payload = {
            "prompt1": "",
            "prompt2": "test",
            "metric": "cosine"
        }
        
        with self.client.post("/api/similarity-check", json=payload, catch_response=True) as response:
            if response.status_code == 400:
                response.success()  # We expect a 400 error
            else:
                response.failure(f"Expected 400 for empty prompt, got {response.status_code}")
    
    @task  
    def test_missing_fields(self):
        """Test missing required fields"""
        payload = {
            "prompt1": "only one prompt"
            # Missing prompt2
        }
        
        with self.client.post("/api/similarity-check", json=payload, catch_response=True) as response:
            if response.status_code == 422:  # Pydantic validation error
                response.success()
            else:
                response.failure(f"Expected 422 for missing field, got {response.status_code}")

# Instructions pour utiliser le load testing:
"""
Commandes pour effectuer le load testing:

1. Test basique (10 utilisateurs, 2 par seconde, 1 minute):
   locust -f tests/load_test/locustfile.py --host=http://localhost:8003 -u 10 -r 2 -t 60s

2. Test de montée en charge (100 utilisateurs, 10 par seconde, 5 minutes):
   locust -f tests/load_test/locustfile.py --host=http://localhost:8003 -u 100 -r 10 -t 300s

3. Test de stress (500 utilisateurs, 50 par seconde, 10 minutes):
   locust -f tests/load_test/locustfile.py --host=http://localhost:8003 -u 500 -r 50 -t 600s

4. Interface web (recommandé):
   locust -f tests/load_test/locustfile.py --host=http://localhost:8003
   Puis ouvrir http://localhost:8089

5. Test spécifique des erreurs:
   locust -f tests/load_test/locustfile.py --host=http://localhost:8003 -u 5 -r 1 -t 30s ErrorTestUser

6. Test haute charge:
   locust -f tests/load_test/locustfile.py --host=http://localhost:8003 -u 50 -r 10 -t 120s HighLoadUser
"""