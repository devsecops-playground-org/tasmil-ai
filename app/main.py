"""HTTP surface of the agent runner."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app import __version__
from app.agents.runner import AgentRunner, UnknownToolError
from app.config import get_settings
from app.models import Health, TaskRequest, TaskResult


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Refuse to serve traffic if production is missing a required secret."""
    missing = get_settings().validate_for_production()
    if missing:
        raise RuntimeError(f"missing required production secrets: {', '.join(missing)}")
    yield


app = FastAPI(title="Tasmil Agent Runner", version=__version__, lifespan=lifespan)


@app.get("/health", response_model=Health, tags=["ops"])
def health() -> Health:
    settings = get_settings()
    return Health(status="ok", environment=settings.app_env, version=__version__)


@app.post("/api/run", response_model=TaskResult, tags=["agent"])
def run_task(request: TaskRequest) -> TaskResult:
    runner = AgentRunner(max_steps=get_settings().max_steps)
    try:
        return runner.run(request)
    except UnknownToolError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/tools", tags=["agent"])
def list_tools() -> dict[str, list[str]]:
    from app.agents.runner import KNOWN_TOOLS

    return {"tools": sorted(KNOWN_TOOLS)}
