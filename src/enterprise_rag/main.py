from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from enterprise_rag.config import settings
from enterprise_rag.data.flight_data import load_flights
from enterprise_rag.database.store import table_ready, row_count, ingest_frame
from enterprise_rag.schemas import QueryRequest, QueryResponse, HealthResponse
from enterprise_rag.auth.security import require_auth
from enterprise_rag.service import RAGService
from enterprise_rag.observability.logging_config import configure_logging
import logging
import time
from uuid import uuid4

configure_logging()
logger = logging.getLogger("enterprise_rag.http")

_service: RAGService | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _service
    if not table_ready(settings.sqlite_path):
        frame = load_flights(settings.data_path)
        ingest_frame(frame, settings.sqlite_path)
    _service = RAGService()
    yield
    _service = None

app = FastAPI(title="Enterprise Hybrid RAG", version="0.1.0", description="Hybrid SQL and semantic retrieval with CRAG-style correction and Self-RAG-style reflection", lifespan=lifespan)

@app.middleware("http")
async def request_logging(request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed request_id=%s method=%s path=%s", request_id, request.method, request.url.path)
        raise
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info("request_complete request_id=%s method=%s path=%s status=%s elapsed_ms=%s", request_id, request.method, request.url.path, response.status_code, elapsed_ms)
    return response

@app.get("/", response_class=HTMLResponse)
async def home():
    return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Enterprise Hybrid RAG</title><style>body{font:16px system-ui;max-width:900px;margin:3rem auto;padding:0 1rem;color:#18212b}textarea{width:100%;min-height:100px;padding:12px}button{padding:10px 16px;cursor:pointer}pre{white-space:pre-wrap;background:#f3f5f7;padding:16px;border-radius:8px}small{color:#555}</style></head><body><h1>Enterprise Hybrid RAG</h1><p>Ask the synthetic flight dataset a question. For local development only; see security documentation before exposing this service.</p><textarea id='q'>Which airline has the highest cancellation rate?</textarea><p><label>API key (only needed when authentication is enabled): <input id='key' type='password' autocomplete='off'></label></p><p><button onclick='ask()'>Ask question</button> <a href='/docs'>API docs</a></p><pre id='out'>Answer will appear here.</pre><script>async function ask(){let q=document.getElementById('q').value;let out=document.getElementById('out');out.textContent='Working…';try{let r=await fetch('/query',{method:'POST',headers:{'Content-Type':'application/json',...(document.getElementById('key').value?{'X-API-Key':document.getElementById('key').value}:{})},body:JSON.stringify({question:q})});let d=await r.json();out.textContent=JSON.stringify(d,null,2)}catch(e){out.textContent='Request failed: '+e}}</script></body></html>"""

@app.get("/health", response_model=HealthResponse)
async def health():
    ready = table_ready(settings.sqlite_path)
    return HealthResponse(status="ok" if ready else "not_ready", database_ready=ready, dataset_rows=row_count(settings.sqlite_path))

@app.get("/ready")
async def ready():
    if not table_ready(settings.sqlite_path): raise HTTPException(status_code=503, detail="Database is not initialized")
    return {"ready":True}

@app.get("/dataset/summary", dependencies=[Depends(require_auth)])
async def dataset_summary():
    frame = load_flights(settings.data_path)
    return {"rows":int(len(frame)),"columns":list(frame.columns),"synthetic_data":True,"statuses":sorted(frame.status.dropna().astype(str).unique().tolist()),"airlines":sorted(frame.airline.dropna().astype(str).unique().tolist())}

@app.post("/query", response_model=QueryResponse, dependencies=[Depends(require_auth)])
async def query(request: QueryRequest):
    if _service is None: raise HTTPException(status_code=503, detail="Application is still starting")
    try:
        return _service.answer(request.question.strip())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Configured dataset is missing") from exc
    except Exception as exc:
        # Avoid returning internal exception details to callers.
        raise HTTPException(status_code=500, detail="Query failed safely; check server logs") from exc
