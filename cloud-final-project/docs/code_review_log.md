# Code review log

## Review 1: API and authentication

- API key is required for upload/list/audit.
- Invocation URL intentionally uses an unguessable token to model public Lambda-style invocation.
- API keys are stored as SHA-256 hashes, not plaintext.

## Review 2: Storage

- Upload archive size is limited.
- Zip extraction defends against path traversal by checking resolved destination paths.

## Review 3: Execution

- User function does not execute inside the FastAPI process.
- Subprocess sandbox has timeout and optional Unix resource limits.
- Production note clearly states Firecracker is required for strong isolation.

## Review 4: Verification

- Static AST analyzer checks handler contract, dangerous imports and dangerous calls.
- Regex analyzer catches suspicious shell/network/secret patterns.
- ClamAV and LLM are adapter-style so real infrastructure can be connected without redesign.


## Review 5: Fix pass

- Fixed the subprocess sandbox so benign handlers execute reliably in normal development environments.
- Added real per-function dependency preparation through `pip --target .oblak-deps`.
- Hardened zip traversal validation by using `Path.relative_to` instead of string prefix matching.
- Scoped the audit endpoint to the authenticated user's events.
- Re-ran the test suite: all tests pass.
