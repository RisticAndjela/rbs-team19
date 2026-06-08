# API examples

## Upload

```bash
curl -X POST http://127.0.0.1:8000/functions \
  -H 'X-API-Key: oblak-dev-key' \
  -F 'name=hello' \
  -F 'file=@hello.zip'
```

## Invoke

```bash
curl -X POST http://127.0.0.1:8000/invoke/<token> \
  -H 'Content-Type: application/json' \
  -d '{"payload":{"name":"Andji"}}'
```
