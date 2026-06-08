from pathlib import Path

from oblak.orchestrator.subprocess_sandbox import SubprocessSandboxOrchestrator


def test_executes_handler(tmp_path: Path):
    (tmp_path / "handler.py").write_text(
        "def handler(event, context):\n    return {'value': event['value'] + 1}\n",
        encoding="utf-8",
    )
    result = SubprocessSandboxOrchestrator().execute(tmp_path, {"value": 41})
    assert result.status == "success"
    assert result.result == {"value": 42}
