# Static analysis report

## Scope

The project source under `oblak/` was scanned with Bandit on 2026-06-26.

Command used:

```bash
PYTHONPATH=.pythonlibs .pythonlibs/bin/bandit.exe -r oblak -f json -o docs/bandit_report.json
```

Raw artifact:

- `docs/bandit_report.json`

## Summary

- Total scanned LOC: 1088
- Total findings: 15
- High severity: 0
- Medium severity: 0
- Low severity: 15

## Finding categories

- `B404` for importing `subprocess`
- `B603` for subprocess execution without `shell=True`
- `B607` for partial executable paths in Firecracker host tooling
- `B110` for one portability-focused `try/except/pass`

## Assessment

The findings are expected in this architecture because the platform intentionally contains code that:

- launches isolated execution backends,
- prepares dependencies with `pip`,
- invokes external host tools for Firecracker integration,
- optionally calls the ClamAV scanner.

These findings are still relevant and should not be ignored blindly, but the 2026-06-26 scan did not detect any medium- or high-severity issues in the application code.

## Follow-up items

- Prefer absolute paths for Firecracker helper binaries where practical to reduce `B607` findings.
- Consider replacing the broad `except Exception: pass` in the subprocess simulator with narrower exception handling plus audit logging.
- In a production deployment, move dependency installation into a disposable builder VM/container and keep Firecracker execution isolated from the API host.
