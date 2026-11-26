from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.domains.haptan_monitor.repository import observation_repository
from src.domains.haptan_monitor.router import router as monitor_router
from src.domains.algae_vision.router import router as algae_vision_router
from src.domains.atmosphere_cycle.repository import atmosphere_repository
from src.domains.atmosphere_cycle.router import router as atmosphere_router

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    observation_repository.initialize()
    atmosphere_repository.initialize()
    yield


app = FastAPI(title="Haptan Monitor", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(algae_vision_router)
app.include_router(monitor_router)
app.include_router(atmosphere_router)


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
