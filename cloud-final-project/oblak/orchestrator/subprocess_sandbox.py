import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Any

from oblak.core.config import get_settings
from oblak.orchestrator.base import ExecutionResult


class SubprocessSandboxOrchestrator:
    """Firecracker simulator.

    This class intentionally keeps the same boundary a real Firecracker orchestrator would have:
    source directory + JSON event in, JSON execution result out. It uses a subprocess sandbox so the
    project is runnable on ordinary development machines.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def execute(self, source_dir: Path, payload: dict[str, Any]) -> ExecutionResult:
        source_dir = source_dir.resolve()
        runner = self._runner_script(source_dir, payload)
        start = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="oblak-run-") as tmp:
            runner_path = Path(tmp) / "runner.py"
            runner_path.write_text(runner, encoding="utf-8")
            try:
                completed = subprocess.run(
                    [sys.executable, str(runner_path)],
                    cwd=tmp,
                    text=True,
                    capture_output=True,
                    timeout=self.settings.execution_timeout_seconds,
                    env=self._restricted_env(source_dir),
                    preexec_fn=self._limit_resources if os.name == "posix" else None,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                return ExecutionResult(
                    status="timeout",
                    duration_ms=self._duration_ms(start),
                    result=None,
                    stdout=(exc.stdout or "")[: self.settings.max_stdout_bytes],
                    stderr="Execution timed out",
                )
        stdout = completed.stdout[: self.settings.max_stdout_bytes]
        stderr = completed.stderr[: self.settings.max_stdout_bytes]
        parsed = self._parse_result(stdout)
        return ExecutionResult(
            status="success" if completed.returncode == 0 and parsed.get("ok") else "error",
            duration_ms=self._duration_ms(start),
            result=parsed.get("result"),
            stdout=stdout,
            stderr=stderr,
        )

    def _runner_script(self, source_dir: Path, payload: dict[str, Any]) -> str:
        payload_json = json.dumps(payload)
        return textwrap.dedent(
            f"""
            import importlib.util
            import json
            import sys
            from pathlib import Path

            source_dir = Path({str(source_dir)!r})
            sys.path.insert(0, str(source_dir))
            spec = importlib.util.spec_from_file_location("handler", source_dir / "handler.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            context = {{"platform": "oblak", "isolation": "subprocess-simulator"}}
            try:
                result = module.handler({payload_json}, context)
                print("__OBLAK_RESULT__" + json.dumps({{"ok": True, "result": result}}, default=str))
            except Exception as exc:
                print("__OBLAK_RESULT__" + json.dumps({{"ok": False, "result": str(exc)}}))
                raise
            """
        )

    def _restricted_env(self, source_dir: Path) -> dict[str, str]:
        return {
            "PYTHONPATH": str(source_dir),
            "PYTHONDONTWRITEBYTECODE": "1",
            "OBLAK_SANDBOX": "1",
        }

    def _limit_resources(self) -> None:
        try:
            import resource

            resource.setrlimit(resource.RLIMIT_CPU, (self.settings.execution_timeout_seconds, self.settings.execution_timeout_seconds + 1))
            resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
            resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
        except Exception:
            pass

    def _parse_result(self, stdout: str) -> dict[str, Any]:
        for line in reversed(stdout.splitlines()):
            if line.startswith("__OBLAK_RESULT__"):
                return json.loads(line.removeprefix("__OBLAK_RESULT__"))
        return {"ok": False, "result": None}

    def _duration_ms(self, start: float) -> int:
        return int((time.perf_counter() - start) * 1000)
