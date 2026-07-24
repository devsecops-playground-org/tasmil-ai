"""The agent loop.

Kept deterministic and model-free so it is testable in CI without network access
or credentials — the interesting behaviour to protect is the step budget and the
tool allow-list, not the model's prose.
"""

from app.models import Outcome, Step, TaskRequest, TaskResult

KNOWN_TOOLS = {"quote", "swap", "balance", "rebalance", "report"}


class UnknownToolError(ValueError):
    def __init__(self, tool: str) -> None:
        super().__init__(f"tool '{tool}' is not available to this runner")
        self.tool = tool


class AgentRunner:
    def __init__(self, max_steps: int = 8) -> None:
        self.max_steps = max_steps

    def plan(self, request: TaskRequest) -> list[str]:
        """Tools to invoke, in order. An empty request plans a single report step."""
        for tool in request.tools:
            if tool not in KNOWN_TOOLS:
                raise UnknownToolError(tool)
        return list(request.tools) or ["report"]

    def run(self, request: TaskRequest) -> TaskResult:
        budget = request.max_steps or self.max_steps
        planned = self.plan(request)

        steps = [
            Step(index=i, tool=tool, summary=f"executed {tool} for: {request.goal[:60]}")
            for i, tool in enumerate(planned[:budget])
        ]

        # Running out of budget is a halt, not a failure: the work so far is valid.
        outcome = Outcome.HALTED if len(planned) > budget else Outcome.COMPLETED
        return TaskResult(goal=request.goal, outcome=outcome, steps=steps)
