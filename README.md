# AI Similarity Service

## Overview

Production-ready microservice for text similarity calculation and LLM processing with comprehensive sanitization, multiple similarity metrics, and robust testing suite.

## Features

- **🔍 Multiple Similarity Metrics**: Cosine, Jaccard, LLM-based, Direct LLM
- **🛡️ Robust Security**: Input/output sanitization, blacklist filtering, length validation
- **⚡ High Performance**: FastAPI framework with async support
- **📊 Load Testing**: Comprehensive Locust-based load testing suite
- **🧪 Full Test Coverage**: Unit, integration, and load tests
- **🐳 Container Ready**: Docker deployment with health checks
- **📖 Auto Documentation**: OpenAPI/Swagger documentation

## Architecture

```
app/
├── core/                 # Core business logic
│   ├── similarity.py     # Similarity calculation algorithms
│   ├── sanitization.py   # Input/output cleaning
│   └── llm_proxy.py      # LLM integration (OpenAI)
├── api/                  # API layer
│   └── endpoints.py      # REST API endpoints
├── config.py             # Configuration management
└── main.py              # FastAPI application

tests/
├── unit/                 # Unit tests
├── integration/          # API integration tests
└── load_test/           # Load testing with Locust
```

## Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (optional, for LLM features)

### 1. Setup Development Environment

```bash
# Clone and setup
git clone <your-repo>
cd ai-similarity-service

# Run automated setup
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Configuration

Create `.env` file:

```env
# Service Configuration
PORT=8003
SIMILARITY_THRESHOLD=0.7
DEFAULT_METRIC=cosine
MAX_INPUT_LENGTH=1000

# Security
BLACKLIST=malicious,harmful,offensive,spam

# LLM Configuration (Optional)
LLM_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo
LLM_MAX_TOKENS=150
LLM_TEMPERATURE=0.7

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
```

### 3. Run the Service

```bash
# Development mode
./start_service.sh

# Or manually
uvicorn app.main:app --port 8003 --reload

# Service available at:
# - API: http://localhost:8003
# - Docs: http://localhost:8003/docs
# - Health: http://localhost:8003/health
```

## API Usage

### Similarity Check Endpoint

**POST** `/api/similarity-check`

**Request:**
```json
{
  "prompt1": "Artificial Intelligence is transforming technology",
  "prompt2": "Machine Learning is revolutionizing computing",
  "metric": "cosine",
  "threshold": 0.7
}
```

**Response:**
```json
{
  "similarity_score": 0.8234,
  "similarity_metric": "cosine",
  "threshold": 0.7,
  "above_threshold": true,
  "llm_response": "Both texts discuss advanced computing technologies...",
  "processing_time_ms": 245
}
```

### Available Similarity Metrics

| Metric | Description | Use Case |
|--------|-------------|----------|
| `cosine` | TF-IDF cosine similarity | General text comparison |
| `jaccard` | Jaccard coefficient | Token-based similarity |
| `llm` | LLM-enhanced cosine | Advanced semantic understanding |
| `direct_llm` | Pure LLM assessment | Highest quality, slower |

### Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Invalid input (validation errors)
- `422`: Malformed request
- `429`: Rate limit exceeded
- `500`: Internal server error

## Testing

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_similarity.py -v
```

### Integration Tests

```bash
# API integration tests
pytest tests/integration/ -v

# Test specific endpoint
pytest tests/integration/test_api.py::test_similarity_endpoint -v
```

### Load Testing

Start the service first, then run load tests:

```bash
# Basic load test (10 users, 60 seconds)
locust -f tests/load_test/locustfile.py --host=http://localhost:8003 -u 10 -r 2 -t 60s

# Stress test (100 users, 5 minutes)
locust -f tests/load_test/locustfile.py --host=http://localhost:8003 -u 100 -r 10 -t 300s

# Web interface (recommended)
locust -f tests/load_test/locustfile.py --host=http://localhost:8003
# Open http://localhost:8089
```

**Load Test Scenarios:**
- **SimilarityServiceUser**: Normal usage patterns
- **HighLoadUser**: Rapid-fire requests for stress testing
- **ErrorTestUser**: Edge cases and error handling

## Deployment

### Docker

```bash
# Build image
docker build -t ai-similarity-service .

# Run container
docker run -p 8003:8003 --env-file .env ai-similarity-service

# With custom environment
docker run -p 8003:8003 \
  -e LLM_API_KEY=your_key \
  -e SIMILARITY_THRESHOLD=0.8 \
  ai-similarity-service
```

### Production Deployment

```bash
# Multi-stage build for production
docker build -f docker/Dockerfile.prod -t ai-similarity-service:prod .

# With docker-compose
docker-compose up -d
```

## Scaling Considerations

### Horizontal Scaling

The service is **stateless** and scales horizontally:

```bash
# Multiple instances behind load balancer
docker run -p 8003:8003 ai-similarity-service
docker run -p 8004:8003 ai-similarity-service  
docker run -p 8005:8003 ai-similarity-service

# Use nginx/HAProxy for load balancing
```

### Performance Optimization

1. **Caching**: Implement Redis for similarity result caching
2. **Connection Pooling**: Use connection pools for LLM API calls
3. **Async Processing**: Queue long-running LLM requests
4. **Database**: Add persistent storage for analytics

### Monitoring

- **Health Checks**: `/health` endpoint for container orchestration
- **Metrics**: Custom metrics endpoint for monitoring
- **Logging**: Structured logging for observability
- **Alerts**: Set up alerts for error rates and response times

## Security Features

### Input Sanitization
- HTML tag removal
- Special character escaping  
- Length validation
- Blacklist word filtering

### Output Sanitization
- Control character removal
- Response length limiting
- Content filtering

### Rate Limiting
- Per-client request limits
- Configurable thresholds
- 429 status code responses

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8003 | Service port |
| `SIMILARITY_THRESHOLD` | 0.7 | Minimum similarity for LLM trigger |
| `DEFAULT_METRIC` | cosine | Default similarity metric |
| `MAX_INPUT_LENGTH` | 1000 | Maximum input text length |
| `BLACKLIST` | "" | Comma-separated forbidden words |
| `LLM_API_KEY` | "" | OpenAI API key |
| `LLM_MODEL` | gpt-3.5-turbo | OpenAI model name |
| `LLM_MAX_TOKENS` | 150 | Maximum LLM response tokens |
| `MAX_REQUESTS_PER_MINUTE` | 60 | Rate limit per client |

## Development

### Code Quality

```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

### Adding New Similarity Metrics

1. Add method to `SimilarityCalculator` class
2. Update valid metrics in `endpoints.py`  
3. Add unit tests
4. Update documentation

## Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check configuration
python -c "from app.config import Config; Config.log_config()"

# Verify dependencies
pip install -r requirements.txt
```

**LLM features not working:**
```bash
# Verify API key
echo $LLM_API_KEY

# Test API connection
curl -H "Authorization: Bearer $LLM_API_KEY" https://api.openai.com/v1/models
```

**High response times:**
- Check LLM API quotas
- Monitor similarity metric performance
- Consider caching strategies

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

---