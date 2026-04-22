.PHONY: build test lint clean check

# Standard execution targets for Agentic OS
# Agents should rely on these instead of guessing build commands.

build:
	@echo "Building application..."
	# TODO: Replace with actual build command (e.g., npm run build, cargo build)

test:
	@echo "Running tests..."
	python -m pytest tests/

lint:
	@echo "Running linters..."
	# TODO: Add linters (e.g., flake8, ruff)

gate:
	@echo "Running Doc Governance Gate..."
	python scripts/docs_gate.py --fast

clean:
	@echo "Cleaning workspace..."
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete