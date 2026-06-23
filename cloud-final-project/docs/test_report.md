# Test report

Command run after the fix pass:

```bash
python -m pytest -q
```

Result:

```text
5 passed
```

Additional validation:

```bash
python -m compileall -q oblak tests
```
