# Oblak Postman demo

Fajlovi u ovom folderu su spremni za lokalni demo aplikacije iz Postmana.

## Sta je dodato

- `collections/oblak-demo.postman_collection.json` - kompletan demo tok.
- `environments/oblak-local.postman_environment.json` - lokalni environment sa `baseUrl`, `apiKey` i putanjama do demo ZIP fajlova.
- `demo-files/benign-hello.zip` - benign upload primer.
- `demo-files/benign-math.zip` - drugi benign primer za invoke sa brojevima.
- `demo-files/malicious-eval.zip` - primer koji verifier treba da odbije.

## Redosled za demo

1. Pokreni backend (`uvicorn oblak.api.main:app --reload`) i inicijalizuj bazu ako vec nije (`python scripts/init_db.py`).
2. U Postmanu izaberi environment `Oblak Local`.
3. Posalji requestove redom:
   `1. Health` -> `2. Upload benign hello` -> `3. List functions` -> `4. Invoke hello` -> `5. Upload benign math` -> `6. Invoke math` -> `7. Upload malicious eval` -> `8. Audit trail`

## Napomene

- Environment je podesen na seed API key `oblak-dev-key`.
- Upload requestovi automatski pamte `invoke_url`, token i ID funkcije za naredne korake.
- Ako se projekat premesti na drugu lokaciju, azuriraj `helloZipPath`, `mathZipPath` i `maliciousZipPath` u environment-u.
