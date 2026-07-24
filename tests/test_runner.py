import pytest

from app.agents.runner import AgentRunner, UnknownToolError
from app.config import Settings
from app.models import Outcome, TaskRequest


def test_an_empty_tool_list_plans_a_report():
    assert AgentRunner().plan(TaskRequest(goal="status")) == ["report"]


def test_unknown_tools_are_rejected_before_anything_runs():
    with pytest.raises(UnknownToolError) as exc:
        AgentRunner().plan(TaskRequest(goal="x", tools=["quote", "drain_wallet"]))
    assert exc.value.tool == "drain_wallet"


def test_a_run_within_budget_completes():
    result = AgentRunner(max_steps=4).run(TaskRequest(goal="rebalance", tools=["quote", "swap"]))
    assert result.outcome is Outcome.COMPLETED
    assert [s.tool for s in result.steps] == ["quote", "swap"]


def test_exceeding_the_step_budget_halts_rather_than_fails():
    result = AgentRunner(max_steps=1).run(TaskRequest(goal="rebalance", tools=["quote", "swap"]))
    assert result.outcome is Outcome.HALTED
    assert len(result.steps) == 1


def test_a_request_may_lower_but_not_raise_its_own_budget():
    result = AgentRunner(max_steps=8).run(
        TaskRequest(goal="g", tools=["quote", "swap", "report"], max_steps=2)
    )
    assert len(result.steps) == 2


def test_api_rejects_an_unknown_tool(client):
    response = client.post("/api/run", json={"goal": "x", "tools": ["nope"]})
    assert response.status_code == 400
    assert "not available" in response.json()["detail"]


def test_api_runs_a_task(client):
    response = client.post("/api/run", json={"goal": "rebalance the vault", "tools": ["quote"]})
    assert response.status_code == 200
    assert response.json()["outcome"] == "completed"


@pytest.mark.parametrize(
    ("env", "anthropic", "openai", "expected"),
    [
        ("development", "", "", 0),
        ("production", "key", "", 0),
        ("production", "", "key", 0),
        ("production", "", "", 1),
    ],
)
def test_production_requires_a_model_credential(env, anthropic, openai, expected):
    settings = Settings(app_env=env, anthropic_api_key=anthropic, openai_api_key=openai)
    assert len(settings.validate_for_production()) == expected
