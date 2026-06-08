# Security requirements

## System-level requirements

1. CDK CLI must authenticate every privileged server operation with an API key.
2. Uploaded archives must be size-limited and safely extracted without path traversal.
3. Every uploaded function must be verified before it can be invoked.
4. Rejected functions must not receive executable status.
5. Invocation must run outside the API server process.
6. Execution must have a timeout, restricted environment and bounded output.
7. Every security-relevant action must be auditable.
8. The API must not expose filesystem paths or raw internal identifiers except controlled function IDs and invocation URLs.

## VM/execution requirements

1. User code must not run inside the web server process.
2. Runtime must provide process isolation.
3. Runtime should deny uncontrolled network and host filesystem access.
4. Runtime should enforce CPU, memory, file descriptor and wall-clock limits.
5. Runtime should return structured stdout, stderr, result and status.
6. Production implementation should replace the simulator with Firecracker microVMs.

## Open production items

- Firecracker jailer configuration.
- Per-function rootfs creation and dependency layering.
- Network namespace isolation.
- Seccomp profile hardening.
- Signed artifacts and immutable versioned storage.
