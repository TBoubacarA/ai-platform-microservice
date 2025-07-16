#!/bin/bash

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Create directory structure
mkdir -p app/core app/api tests/unit tests/integration tests/load_test docker

# Create main files
touch app/__init__.py app/config.py app/main.py
touch app/core/__init__.py app/core/similarity.py app/core/sanitization.py app/core/llm_proxy.py
touch app/api/__init__.py app/api/endpoints.py

# Create test files
touch tests/__init__.py
touch tests/unit/test_similarity.py tests/unit/test_sanitization.py tests/unit/test_llm_proxy.py
touch tests/integration/test_api.py
touch tests/load_test/locustfile.py

# Create config files
touch .env .gitignore requirements.txt docker/Dockerfile README.md start_service.sh

# Populate .gitignore
echo "venv/" > .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.swp" >> .gitignore

# Basic requirements
echo "fastapi" > requirements.txt
echo "uvicorn" >> requirements.txt
echo "python-dotenv" >> requirements.txt
echo "numpy" >> requirements.txt
echo "scikit-learn" >> requirements.txt
echo "sentence-transformers" >> requirements.txt
echo "openai" >> requirements.txt
echo "pytest" >> requirements.txt
echo "locust" >> requirements.txt
echo "requests" >> requirements.txt

# Install dependencies
pip3 install -r requirements.txt

# Create start service script
echo '#!/bin/bash' > start_service.sh
echo 'source venv/bin/activate' >> start_service.sh
echo 'uvicorn app.main:app --port $PORT' >> start_service.sh
chmod +x start_service.sh

echo ""
echo "Setup completed successfully!"
echo "Next steps:"
echo "1. Edit the .env file with your configuration"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Start service: ./start_service.sh"
echo "4. Run tests: pytest tests/"