"""Agent-run schema."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Outcome(StrEnum):
    COMPLETED = "completed"
    HALTED = "halted"
    FAILED = "failed"


class TaskRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=2000)
    tools: list[str] = Field(default_factory=list, max_length=32)
    max_steps: int | None = Field(default=None, ge=1, le=64)


class Step(BaseModel):
    index: int
    tool: str
    summary: str


class TaskResult(BaseModel):
    goal: str
    outcome: Outcome
    steps: list[Step]
    finished_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Health(BaseModel):
    status: str
    environment: str
    version: str
