"""ReviewLens V2 — FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.analyse import router as analyse_router
from app.api.brief import router as brief_router
from app.api.ocr import router as ocr_router

app = FastAPI(
    title="ReviewLens API",
    version="2.0.0",
    description="Customer Voice Insights — upload reviews, get prioritised fix-first recommendations.",
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(analyse_router, prefix="/api")
app.include_router(brief_router, prefix="/api")
app.include_router(ocr_router, prefix="/api")
