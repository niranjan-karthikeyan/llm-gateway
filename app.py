from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Header, HTTPException, Depends, Request
from pydantic import BaseModel
from model import generate
import os
import redis
import json
import time
import uuid
import logging

app = FastAPI()
Instrumentator().instrument(app).expose(app)

logger = logging.getLogger("llm-gateway")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

@app.middleware("http")
async def log_requests(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    log_entry = {
        "correlation_id": correlation_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }
    logger.info(json.dumps(log_entry))

    response.headers["X-Correlation-ID"] = correlation_id
    return response

redis_client = redis.Redis(host="localhost", port=6380, db=0, decode_responses=True)

RATE_LIMIT = 5
WINDOW_SECONDS = 600

def check_rate_limit(x_api_key: str = Header(...)):
    key = f"ratelimit:{x_api_key}"
    count = redis_client.incr(key)
    print(f"[rate-limit] key={key} count={count}")
    if count == 1:
        redis_client.expire(key, WINDOW_SECONDS)
    if count > RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limt exceeded")

API_KEY = os.environ.get("API_KEY")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.get("/health")
def health():
    return {"status": "ok"}

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 50

class CompletionResponse(BaseModel):
    completion: str

@app.post("/v1/completions")
def completions(body: CompletionRequest, _: None = Depends(verify_api_key), __: None = Depends(check_rate_limit)) -> CompletionResponse:
    result = generate(body.prompt, body.max_tokens)
    return CompletionResponse(completion=result)