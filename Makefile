TESTS = tests

VENV ?= .venv
CODE = tests app

HOST = 0.0.0.0
PORT = 8000
WORKERS_NUMBER = 10


.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv:
	python3.9 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

.PHONY: test
test: ## Runs pytest
	$(VENV)/bin/pytest -v tests

.PHONY: test-lf
test-lf: ## Runs pytest (last failure)
	$(VENV)/bin/pytest -v --lf tests
	
.PHONY: lint
lint: ## Lint code
	$(VENV)/bin/flake8 --jobs 4 --statistics --show-source $(CODE)
	$(VENV)/bin/pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	$(VENV)/bin/mypy $(CODE)
	$(VENV)/bin/black --skip-string-normalization --check $(CODE)

.PHONY: format
format: ## Formats all files
	$(VENV)/bin/isort $(CODE)
	$(VENV)/bin/black --skip-string-normalization $(CODE)
	$(VENV)/bin/autoflake --recursive --in-place --remove-all-unused-imports $(CODE)
	$(VENV)/bin/unify --in-place --recursive $(CODE)

.PHONY: ci
ci:	lint test ## Lint code then run tests


.PHONY: up
up: ## Run application
	$(VENV)/bin/uvicorn --reload --factory app.app:create_app --host $(HOST) --port $(PORT)


.PHONY: docker-build
docker-build: ## Build docker image
	docker-compose build

.PHONY: docker-run
docker-run: ## Run docker container
	docker-compose up
