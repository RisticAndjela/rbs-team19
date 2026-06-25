import base64
import json
import os
import shutil
import socket
import subprocess
import tempfile
import textwrap
import time
import uuid
from http.client import HTTPConnection
from pathlib import Path
from typing import Any

from oblak.core.config import get_settings
from oblak.orchestrator.base import ExecutionResult


class FirecrackerConfigurationError(RuntimeError):
    pass


class UnixSocketHTTPConnection(HTTPConnection):
    """Tiny Firecracker API client transport over a Unix domain socket."""

    def __init__(self, socket_path: Path) -> None:
        super().__init__("localhost")
        self.socket_path = str(socket_path)

    def connect(self) -> None:  # pragma: no cover - needs a real Firecracker process
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)


class FirecrackerAPIClient:
    def __init__(self, socket_path: Path) -> None:
        self.socket_path = socket_path

    def put(self, path: str, body: dict[str, Any]) -> None:
        self._request("PUT", path, body)

    def patch(self, path: str, body: dict[str, Any]) -> None:
        self._request("PATCH", path, body)

    def _request(self, method: str, path: str, body: dict[str, Any]) -> None:
        payload = json.dumps(body).encode("utf-8")
        conn = UnixSocketHTTPConnection(self.socket_path)
        try:
            conn.request(
                method,
                path,
                body=payload,
                headers={"Content-Type": "application/json", "Content-Length": str(len(payload))},
            )
            response = conn.getresponse()
            response_body = response.read().decode("utf-8", errors="replace")
            if response.status >= 300:
                raise FirecrackerConfigurationError(
                    f"Firecracker API {method} {path} failed with {response.status}: {response_body}"
                )
        finally:
            conn.close()


class FirecrackerOrchestrator:
    """Execute uploaded Python functions inside a Firecracker microVM.

    This orchestrator expects a prepared guest root filesystem. The guest init must mount the
    read-only code drive, execute ``handler.py`` with the payload from kernel command line and
    print a line prefixed with ``__OBLAK_RESULT__`` to the serial console before shutting down.

    The host side deliberately does not mount source directories into the VM. Instead, every
    invocation creates a disposable ext4 image with the uploaded function code and attaches it as
    a read-only secondary block device. That is the main security boundary: the guest sees only
    its root filesystem and this per-invocation code drive, not the host project storage tree.
    """

    RESULT_PREFIX = "__OBLAK_RESULT__"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._validate_host_configuration()

    def execute(self, source_dir: Path, payload: dict[str, Any]) -> ExecutionResult:
        source_dir = source_dir.resolve()
        start = time.perf_counter()
        vm_id = f"oblak-{uuid.uuid4().hex}"

        with tempfile.TemporaryDirectory(prefix=f"{vm_id}-") as tmp_name:
            tmp = Path(tmp_name)
            api_socket = tmp / "firecracker.socket"
            log_path = tmp / "firecracker.log"
            metrics_path = tmp / "metrics.json"
            serial_path = tmp / "serial.log"
            code_image = tmp / "code.ext4"

            try:
                self._create_code_image(source_dir, code_image)
                process = self._start_firecracker(api_socket, log_path, metrics_path, serial_path)
                try:
                    self._configure_vm(api_socket, code_image, payload, vm_id)
                    stdout, stderr = self._wait_for_vm(process, serial_path, start)
                finally:
                    self._terminate_process(process)
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    status="timeout",
                    duration_ms=self._duration_ms(start),
                    result=None,
                    stdout=self._read_text(serial_path),
                    stderr="Execution timed out inside Firecracker microVM",
                )
            except Exception as exc:
                return ExecutionResult(
                    status="error",
                    duration_ms=self._duration_ms(start),
                    result=None,
                    stdout=self._read_text(serial_path),
                    stderr=str(exc),
                )

        parsed = self._parse_result(stdout)
        return ExecutionResult(
            status="success" if parsed.get("ok") else "error",
            duration_ms=self._duration_ms(start),
            result=parsed.get("result"),
            stdout=stdout[: self.settings.max_stdout_bytes],
            stderr=stderr[: self.settings.max_stdout_bytes],
        )

    def _validate_host_configuration(self) -> None:
        if os.name != "posix":
            raise FirecrackerConfigurationError("Firecracker backend requires a Linux/POSIX host")
        if not Path("/dev/kvm").exists():
            raise FirecrackerConfigurationError("/dev/kvm is missing; enable KVM or use subprocess backend")
        for path, label in [
            (self.settings.firecracker_binary, "Firecracker binary"),
            (self.settings.firecracker_kernel_image, "Firecracker kernel image"),
            (self.settings.firecracker_rootfs_image, "Firecracker rootfs image"),
        ]:
            if not path or not Path(path).exists():
                raise FirecrackerConfigurationError(f"{label} is not configured or does not exist: {path}")
        for tool in ["mkfs.ext4", "debugfs"]:
            if shutil.which(tool) is None:
                raise FirecrackerConfigurationError(f"Required host tool is missing: {tool}")

    def _start_firecracker(
        self, api_socket: Path, log_path: Path, metrics_path: Path, serial_path: Path
    ) -> subprocess.Popen[str]:
        cmd = [str(self.settings.firecracker_binary), "--api-sock", str(api_socket)]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=serial_path.open("w", encoding="utf-8"),
            stderr=subprocess.PIPE,
            text=True,
        )

        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if api_socket.exists():
                break
            if process.poll() is not None:
                _, stderr = process.communicate(timeout=1)
                raise FirecrackerConfigurationError(f"Firecracker exited early: {stderr}")
            time.sleep(0.05)
        else:
            self._terminate_process(process)
            raise FirecrackerConfigurationError("Firecracker API socket was not created")

        client = FirecrackerAPIClient(api_socket)
        client.put(
            "/logger",
            {
                "log_path": str(log_path),
                "level": self.settings.firecracker_log_level,
                "show_level": True,
                "show_log_origin": True,
            },
        )
        client.put("/metrics", {"metrics_path": str(metrics_path)})
        return process

    def _configure_vm(
        self, api_socket: Path, code_image: Path, payload: dict[str, Any], vm_id: str
    ) -> None:
        client = FirecrackerAPIClient(api_socket)
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
        boot_args = " ".join(
            [
                "console=ttyS0",
                "reboot=k",
                "panic=1",
                "pci=off",
                "init=/sbin/oblak-init",
                f"oblak_payload_b64={payload_b64}",
            ]
        )

        client.put(
            "/boot-source",
            {
                "kernel_image_path": str(self.settings.firecracker_kernel_image),
                "boot_args": boot_args,
            },
        )
        client.put(
            "/drives/rootfs",
            {
                "drive_id": "rootfs",
                "path_on_host": str(self.settings.firecracker_rootfs_image),
                "is_root_device": True,
                "is_read_only": self.settings.firecracker_rootfs_read_only,
            },
        )
        client.put(
            "/drives/code",
            {
                "drive_id": "code",
                "path_on_host": str(code_image),
                "is_root_device": False,
                "is_read_only": True,
            },
        )
        client.put(
            "/machine-config",
            {
                "vcpu_count": self.settings.firecracker_vcpu_count,
                "mem_size_mib": self.settings.firecracker_mem_size_mib,
                "smt": False,
                "track_dirty_pages": False,
            },
        )
        if self.settings.firecracker_jailer_chroot_base:
            # The preferred production setup is to start Firecracker through jailer outside
            # this process manager. This setting is documented so students can explain it,
            # but API-socket configuration stays identical after jailer starts the VM.
            pass
        client.patch("/vm", {"state": "Resumed"})

    def _wait_for_vm(
        self, process: subprocess.Popen[str], serial_path: Path, start: float
    ) -> tuple[str, str]:
        timeout = self.settings.execution_timeout_seconds + self.settings.firecracker_boot_timeout_seconds
        try:
            _, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._terminate_process(process)
            raise
        stdout = self._read_text(serial_path)
        stderr = (stderr or "") + self._read_text(serial_path.with_name("firecracker.log"))
        return stdout[: self.settings.max_stdout_bytes], stderr[: self.settings.max_stdout_bytes]

    def _create_code_image(self, source_dir: Path, image_path: Path) -> None:
        size_mb = self.settings.firecracker_code_image_size_mb
        subprocess.run(["truncate", "-s", f"{size_mb}M", str(image_path)], check=True)
        subprocess.run(["mkfs.ext4", "-q", "-F", str(image_path)], check=True)

        commands = ["mkdir /function"]
        for path in sorted(source_dir.rglob("*")):
            if path.name == "source.zip" or "__pycache__" in path.parts:
                continue
            relative = path.relative_to(source_dir)
            target = "/function/" + str(relative).replace(os.sep, "/")
            if path.is_dir():
                commands.append(f"mkdir {target}")
            elif path.is_file():
                commands.append(f"write {path} {target}")
        debugfs_input = "\n".join(commands) + "\n"
        completed = subprocess.run(
            ["debugfs", "-w", str(image_path)],
            input=debugfs_input,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise FirecrackerConfigurationError(
                "Failed to populate function code image: " + completed.stderr[-2000:]
            )

    def _parse_result(self, stdout: str) -> dict[str, Any]:
        for line in reversed(stdout.splitlines()):
            if self.RESULT_PREFIX in line:
                payload = line.split(self.RESULT_PREFIX, 1)[1]
                try:
                    return json.loads(payload)
                except json.JSONDecodeError:
                    return {"ok": False, "result": None}
        return {"ok": False, "result": None}

    def _terminate_process(self, process: subprocess.Popen[str]) -> None:
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)

    def _read_text(self, path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="replace")[: self.settings.max_stdout_bytes]

    def _duration_ms(self, start: float) -> int:
        return int((time.perf_counter() - start) * 1000)
