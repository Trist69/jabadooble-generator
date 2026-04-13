from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routes import health, engine, libraries, images, games, settings

app = FastAPI(title="Dobble Generator API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded/generated assets
_assets = Path("/app/data/assets")
_assets.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")

app.include_router(health.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(engine.router, prefix="/api")
app.include_router(libraries.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(games.router, prefix="/api")
