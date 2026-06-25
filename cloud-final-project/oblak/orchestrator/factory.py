from oblak.core.config import get_settings
from oblak.orchestrator.base import Orchestrator
from oblak.orchestrator.subprocess_sandbox import SubprocessSandboxOrchestrator


def create_orchestrator() -> Orchestrator:
    """Create the configured execution backend.

    The subprocess backend is kept as the portable development/test backend. Set
    ``OBLAK_EXECUTION_BACKEND=firecracker`` on a Linux host with KVM, Firecracker,
    a kernel image and a prepared root filesystem to execute functions in a real microVM.
    """
    settings = get_settings()
    backend = settings.execution_backend.lower().strip()

    if backend == "subprocess":
        return SubprocessSandboxOrchestrator()
    if backend == "firecracker":
        from oblak.orchestrator.firecracker import FirecrackerOrchestrator

        return FirecrackerOrchestrator()

    raise ValueError(f"Unsupported OBLAK_EXECUTION_BACKEND={settings.execution_backend!r}")
