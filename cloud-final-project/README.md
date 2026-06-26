# Oblak™

Oblak is an academic serverless platform inspired by AWS Lambda / Google Cloud Functions. It lets a user upload Python function code through a CDK CLI, verifies it, prepares it, creates an invocation URL and runs it on demand.

This implementation follows the project scope from the specification: authentication, code upload, code verification, dependency preparation, invocation URL creation, on-demand execution, auditability, threat modelling, STRIDE documentation and malicious/benign examples.

Verification artifacts for the written report are stored in `docs/`, including `docs/test_report.md`, `docs/static_analysis_report.md` and the raw Bandit output `docs/bandit_report.json`.

## Architecture

- **Server:** FastAPI REST API.
- **CDK CLI:** Typer-based console app.
- **Storage:** local filesystem storage under `OBLAK_STORAGE_ROOT`.
- **Database:** SQLAlchemy; SQLite by default, PostgreSQL-compatible via `OBLAK_DATABASE_URL`.
- **Code verifier:** static AST/rule checks, regex checks, optional ClamAV scan, optional/mock LLM analyzer adapter.
- **Execution:** configurable orchestrator. `subprocess` is the default portable development backend; `firecracker` starts a disposable Firecracker microVM per invocation on Linux/KVM hosts.
- **Dependency preparation:** optional `requirements.txt` installation into a per-function `.oblak-deps` directory, not into the server runtime.
- **Audit:** database-backed audit events for authentication, upload, verification, preparation and invocation.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
python scripts/init_db.py
uvicorn oblak.api.main:app --reload
```

Default API key seeded by `scripts/init_db.py`:

```text
oblak-dev-key
```

Deploy and invoke the benign example:

```bash
oblak-cdk configure --server-url http://127.0.0.1:8000 --api-key oblak-dev-key
oblak-cdk deploy examples/benign_hello --name hello
oblak-cdk invoke hello --payload '{"name":"Andji"}'
```

## Function format

Uploaded functions must contain `handler.py` with a callable:

```python
def handler(event, context):
    return {"message": "hello", "input": event}
```

`requirements.txt` is optional.

## Execution backend

By default, the project uses the portable subprocess sandbox so the API, CLI and tests run on ordinary development machines:

```bash
export OBLAK_EXECUTION_BACKEND=subprocess
```

To use real Firecracker isolation on a Linux/KVM host, prepare a Firecracker binary, kernel image and root filesystem image, then run:

```bash
export OBLAK_EXECUTION_BACKEND=firecracker
export OBLAK_FIRECRACKER_BINARY=/usr/local/bin/firecracker
export OBLAK_FIRECRACKER_KERNEL_IMAGE=./firecracker/vmlinux
export OBLAK_FIRECRACKER_ROOTFS_IMAGE=./firecracker/rootfs.ext4
```

See `docs/firecracker_integration.md` for the complete host setup, execution pipeline and defence notes.

## Security note

The subprocess backend is intentionally kept as a simulator for portability. It is not equivalent to VM isolation. The Firecracker backend runs uploaded code inside a fresh microVM with a read-only per-invocation code drive and no host directory mount. Dependency installation is functional, but still belongs in a disposable build VM/container in production.
