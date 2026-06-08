# Oblak™

Oblak is an academic serverless platform inspired by AWS Lambda / Google Cloud Functions. It lets a user upload Python function code through a CDK CLI, verifies it, prepares it, creates an invocation URL and runs it on demand.

This implementation follows the project scope from the specification: authentication, code upload, code verification, dependency preparation, invocation URL creation, on-demand execution, auditability, threat modelling, STRIDE documentation and malicious/benign examples.

## Architecture

- **Server:** FastAPI REST API.
- **CDK CLI:** Typer-based console app.
- **Storage:** local filesystem storage under `OBLAK_STORAGE_ROOT`.
- **Database:** SQLAlchemy; SQLite by default, PostgreSQL-compatible via `OBLAK_DATABASE_URL`.
- **Code verifier:** static AST/rule checks, regex checks, optional ClamAV scan, optional/mock LLM analyzer adapter.
- **Execution:** simulator Firecracker orchestrator using a subprocess sandbox with timeout, isolated working directory, restricted environment and optional Unix resource limits.
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

## Security note

The current orchestrator is intentionally a **simulator**. It documents where real Firecracker microVM integration belongs, but does not require Linux KVM or root access. For production, replace `SubprocessSandboxOrchestrator` with a Firecracker-backed implementation and enforce network/filesystem/kernel isolation at the VM level.
