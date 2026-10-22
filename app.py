from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
from pydantic import BaseModel
from model import generate

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health():
    return {"status": "ok"}

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 50

class CompletionResponse(BaseModel):
    completion: str

@app.post("/v1/completions")
def completions(request: CompletionRequest) -> CompletionResponse:
    result = generate(request.prompt, request.max_tokens)
    return CompletionResponse(completion=result)