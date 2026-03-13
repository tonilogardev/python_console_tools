PYTHON ?= python
VENV ?= .venv

.PHONY: install lint format type test coverage security audit check pre-commit

install:
\t$(PYTHON) -m pip install -e .[dev]
\tpre-commit install

lint:
\truff check src tests

format:
\truff format src tests

type:
\tmypy src

test:
\tpytest

coverage:
\tcoverage run -m pytest
\tcoverage report

security:
\tbandit -r src

audit:
\tpip-audit

check: lint type test
\t@echo \"All checks passed\"
