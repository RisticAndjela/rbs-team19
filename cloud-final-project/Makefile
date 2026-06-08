.PHONY: run init test lint security

init:
	python scripts/init_db.py

run:
	uvicorn oblak.api.main:app --reload

test:
	pytest -q

lint:
	ruff check oblak tests

security:
	bandit -r oblak
