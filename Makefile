.PHONY: help install install-dev test test-cov lint format security clean run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test: ## Run tests
	python -m pytest -v

test-cov: ## Run tests with coverage
	python -m pytest -v --cov=app --cov-report=html --cov-report=term-missing

lint: ## Run linting
	flake8 app/ tests/
	black --check app/ tests/
	isort --check-only app/ tests/

format: ## Format code
	black app/ tests/
	isort app/ tests/

security: ## Run security checks
	safety check
	bandit -r app/ -ll

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

run: ## Run the application
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-docker: ## Run with Docker
	docker-compose up --build

test-docker: ## Run tests in Docker
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

ci: ## Run all CI checks locally
	make lint
	make security
	make test-cov
