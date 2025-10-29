from fastapi import FastAPI
from app.routers.uploads import router as uploads_router

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="RAG MVP Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}

# Alle Routen hier “zusammenstecken”
app.include_router(uploads_router, prefix="/api")
