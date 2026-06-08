# STRIDE threat model

## Assets

- User API keys.
- Uploaded Python source archives.
- Prepared function artifacts.
- Invocation URL tokens.
- Audit logs.
- Server host and database.

## Trust boundaries

1. CDK CLI to API server over HTTP.
2. API server to local storage/database.
3. API server to code verifier.
4. API server to execution orchestrator.
5. Orchestrator to untrusted user code.

## STRIDE analysis

| Category | Threat | Mitigation in implementation | Open production item |
|---|---|---|---|
| Spoofing | Attacker deploys code as another user | `X-API-Key` authentication with hashed stored keys | Rotation, scoped keys, mTLS |
| Tampering | Zip path traversal overwrites host files | Safe extraction validates resolved paths | Signed artifacts |
| Repudiation | User denies upload/invocation | `AuditEvent` records upload, verification and invocation | Append-only external audit sink |
| Information disclosure | User code reads server env/files | Subprocess runs with restricted env and isolated cwd | Firecracker rootfs, seccomp, jailer |
| Denial of service | Infinite loop or huge output | Timeout, CPU/memory limits, stdout cap | Queueing, quotas, rate limits |
| Elevation of privilege | Malicious code calls shell/native APIs | Static, regex, ClamAV/mock LLM checks reject high severity findings | Kernel-level VM isolation |

## Malicious test cases

- `examples/malicious_eval`: rejected because of `eval`.
- `examples/malicious_subprocess`: rejected because of `subprocess` import/use.
