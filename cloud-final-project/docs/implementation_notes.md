# Implementation notes

## Why the orchestrator is simulated

The project specification recommends Firecracker for unsafe code execution, but real Firecracker requires Linux KVM access, root/jailer setup and a prepared microVM root filesystem. This implementation keeps the same architectural seam through an `Orchestrator` protocol and a `SubprocessSandboxOrchestrator`. That makes the project runnable in a normal academic/dev environment while documenting the exact replacement point for real Firecracker.

## Dependency preparation

When `requirements.txt` is present, the server installs dependencies into `.oblak-deps` inside the stored function artifact using `pip --target`. The subprocess runner prepends this directory to `PYTHONPATH`. This completes the academic preparation flow while keeping the production note clear: a real deployment should build this layer inside a disposable builder and attach it to a Firecracker root filesystem.

## Clean-code structure

- `oblak/api`: HTTP routes and app factory.
- `oblak/cli`: CDK CLI.
- `oblak/core`: configuration.
- `oblak/db`: database session and initialization.
- `oblak/models`: database entities.
- `oblak/orchestrator`: execution boundary.
- `oblak/security`: authentication.
- `oblak/services`: application use cases.
- `oblak/storage`: code artifact storage.
- `oblak/verifier`: antivirus/static/regex/LLM verification pipeline.
- `docs`: security requirements, STRIDE model, review log and API examples.
- `examples`: benign and malicious functions.
- `tests`: verifier, orchestrator and API tests.
