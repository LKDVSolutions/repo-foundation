.PHONY: build test lint clean aggregate gate drift propose check

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

aggregate:
	@echo "Aggregating registry from frontmatter..."
	python scripts/aggregate_registry.py

gate: aggregate
	@echo "Running Doc Governance Gate..."
	python scripts/docs_gate.py --fast

drift:
	@echo "Running drift detection..."
	python scripts/detect_drift.py

propose:
	@echo "Proposing fixes to .shadow/ (no source files modified)..."
	python scripts/propose_fixes.py --report

check: aggregate gate drift
	@echo "Full governance check complete."

clean:
	@echo "Cleaning workspace..."
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete