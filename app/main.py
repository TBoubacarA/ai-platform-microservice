from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.endpoints import router as api_router
from app.config import Config

app = FastAPI(
    title="AI Similarity Service",
    description="Microservice for text similarity and LLM processing",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy", "port": Config.PORT}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>AI Similarity Service</title>
        </head>
        <body>
            <h1>AI Similarity Service</h1>
            <p>Service is running successfully!</p>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/health">Health Check</a></li>
                <li>POST endpoint: <code>/api/similarity-check</code></li>
            </ul>
        </body>
    </html>
    """