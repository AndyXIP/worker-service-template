#!/usr/bin/env bash
#MISE description="Lint/Type check with ruff and ty"
echo "Running ruff..."
ruff check src/ tests/
ruff format --check src/ tests/

echo "Running ty..."
mise run typecheck
