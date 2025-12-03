PYTHON = uv run python
MANAGE = $(PYTHON) manage.py

.PHONY: install run migrate makemigrations worker beat test shell

install:
	uv sync

run:
	$(MANAGE) runserver 0.0.0.0:8000

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

worker:
	uv run celery -A config worker -l info

beat:
	uv run celery -A config beat -l info

test:
	$(MANAGE) test

shell:
	$(MANAGE) shell


