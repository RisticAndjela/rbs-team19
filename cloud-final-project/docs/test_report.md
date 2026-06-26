# Test report

Validation run on 2026-06-26 after the security/documentation pass:

```bash
PYTHONPATH=.pythonlibs .pythonlibs/bin/pytest.exe -q
```

Result:

```text
5 passed, 1 warning
```

Additional validation:

```bash
python -m compileall -q oblak tests
```

## Static analysis

Command:

```bash
PYTHONPATH=.pythonlibs .pythonlibs/bin/bandit.exe -r oblak -f json -o docs/bandit_report.json
```

Result summary:

```text
Bandit reported 15 LOW severity findings, 0 MEDIUM, 0 HIGH.
```

Interpretation:

- The reported findings are concentrated around the intentional process-execution boundary: Firecracker orchestration, subprocess sandboxing, dependency installation and the optional ClamAV adapter.
- No medium- or high-severity issues were reported in the scanned `oblak` package.
- The raw scan artifact is committed as `docs/bandit_report.json`.
