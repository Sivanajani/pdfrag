import asyncio
import logging
import os
import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers.uploads import router as uploads_router
from app.routers.llm import router as llm_router
from app.utils.paths import cleanup_tmp, TMP_MAX_AGE_SECONDS

logger = logging.getLogger(__name__)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",")

# Rate limiting config (requests per minute for /api/llm/* endpoints)
LLM_RATE_LIMIT = int(os.getenv("LLM_RATE_LIMIT", "30"))
LLM_RATE_WINDOW = 60  # seconds

app = FastAPI(
    title="RAG MVP Backend",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# --- Rate limiting middleware (in-memory, per IP) ---

_rate_store: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def rate_limit_llm(request: Request, call_next):
    if request.url.path.startswith("/api/llm/"):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - LLM_RATE_WINDOW

        # Clean old entries and check count
        timestamps = _rate_store[client_ip]
        _rate_store[client_ip] = [t for t in timestamps if t > window_start]

        if len(_rate_store[client_ip]) >= LLM_RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit erreicht. Max. {LLM_RATE_LIMIT} Anfragen pro Minute."},
            )

        _rate_store[client_ip].append(now)

    return await call_next(request)


# --- Health checks ---

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# --- Routers ---

app.include_router(uploads_router, prefix="/api")
app.include_router(llm_router, prefix="/api")


# --- Startup: cleanup old tmp files + periodic cleanup task ---

@app.on_event("startup")
async def startup_cleanup():
    deleted = cleanup_tmp()
    if deleted:
        logger.info("Startup cleanup: %d alte tmp-Dateien geloescht", deleted)

    async def periodic_cleanup():
        while True:
            await asyncio.sleep(TMP_MAX_AGE_SECONDS)
            try:
                cleanup_tmp()
            except Exception:
                logger.exception("Periodischer tmp-Cleanup fehlgeschlagen")

    asyncio.create_task(periodic_cleanup())
