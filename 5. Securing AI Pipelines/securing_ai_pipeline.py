import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, Field, ValidationError
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import requests
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import re
import uvicorn
from contextlib import asynccontextmanager

# Constants
TOGETHER_AI_ENDPOINT = "https://api.together.xyz/v1/chat/completions"
CHAT_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
SENTIMENT_MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"
REQUEST_TIMEOUT = 30
MAX_PROMPT_LENGTH = 500

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("TOGETHER_API_KEY")
if not API_KEY:
    logger.error("TOGETHER_API_KEY not found in environment variables")
    raise ValueError("TOGETHER_API_KEY is required")

# Lifespan handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Secure AI Pipeline API started")
    yield
    # Shutdown logic
    logger.info("Secure AI Pipeline API shutting down")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Secure AI Pipeline",
    description="A secure API for AI predictions and sentiment analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Load sentiment analysis model once at startup
try:
    tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL)
    sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
except Exception as e:
    logger.error(f"Failed to load sentiment model: {e}")
    raise RuntimeError("Sentiment model initialization failed")

# Pydantic Models
class UserQuery(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=MAX_PROMPT_LENGTH, description="User input prompt")

    @classmethod
    def validate_prompt(cls, value: str) -> str:
        dangerous_patterns = [r"<script>", r"SELECT.*FROM", r"DROP TABLE", r"eval\("]
        if any(re.search(pattern, value, re.IGNORECASE) for pattern in dangerous_patterns):
            raise ValueError("Input contains potentially malicious content")
        return value

class InputData(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=MAX_PROMPT_LENGTH)
    api_key: str

class TextInput(BaseModel):
    text: str = Field(..., min_length=1)

class QueryResponse(BaseModel):
    response: str

# Utility Functions
def sanitize_input(prompt: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    try:
        return UserQuery(prompt=prompt).prompt
    except ValidationError as e:
        raise ValueError(f"Invalid input: {e}")

def authenticate(api_key: str) -> bool:
    """Authenticate API key against stored key."""
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return True

# API Endpoints
@app.get("/")
def read_root():
    """Root endpoint for health check."""
    return {"message": "AI Demo App Running"}

@app.post("/predict", response_model=QueryResponse)
async def predict(data: InputData, auth: bool = Depends(authenticate)):
    """Generate a prediction using Together AI API."""
    logger.info(f"Processing predict: {data.prompt[:50]}...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful, honest, and harmless assistant."},
            {"role": "user", "content": data.prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    try:
        response = requests.post(TOGETHER_AI_ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return QueryResponse(response=content)
    except requests.RequestException as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=503, detail=f"Together AI API error: {str(e)}")

@app.post("/analyze_sentiment")
async def analyze_sentiment(input: TextInput):
    """
    Analyze sentiment of text using BERT-based multilingual model.
    Returns sentiment on a 1-5 star scale:
    - 1 star: Highly negative
    - 2 stars: Negative
    - 3 stars: Neutral
    - 4 stars: Positive
    - 5 stars: Highly positive
    """
    logger.info(f"Processing sentiment analysis: {input.text[:50]}...")
    try:
        result = sentiment_analyzer(input.text)
        return {"text": input.text, "sentiment": result[0]["label"]}
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis error: {str(e)}")

@app.post("/query/", response_model=QueryResponse)
@limiter.limit("5/minute")
async def process_query(query: UserQuery, request: Request):
    """Query Together AI model with rate limiting -- 5 requests per minute."""
    response_text = await query_model(query.prompt)
    return QueryResponse(response=response_text)

async def query_model(prompt: str) -> str:
    """Internal function to query Together AI model."""
    sanitized_prompt = sanitize_input(prompt)
    logger.info(f"Processing query_model: {sanitized_prompt[:50]}...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": CHAT_MODEL,
        "messages": [{"role": "user", "content": sanitized_prompt}],
        "max_tokens": 500,
        "temperature": 0.7,
    }
    try:
        response = requests.post(TOGETHER_AI_ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to query model: {str(e)}")
    except KeyError as e:
        logger.error(f"Unexpected response format: {e}")
        raise HTTPException(status_code=500, detail="Invalid response from API")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# uvicorn main:app --reload
# http://127.0.0.1:8000/docs