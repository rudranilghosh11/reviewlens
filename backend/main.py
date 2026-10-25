from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import analyse

app = FastAPI(title="Review Lens API", version="0.1.0")

# CORS for local dev (frontend on http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyse.router, prefix="/api")
