from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    duration_ms: int
    result: Any
    stdout: str
    stderr: str


class Orchestrator(Protocol):
    def execute(self, source_dir: Path, payload: dict[str, Any]) -> ExecutionResult:
        raise NotImplementedError
