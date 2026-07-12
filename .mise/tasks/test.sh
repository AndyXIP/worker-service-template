#!/usr/bin/env bash
#MISE description="Run tests"
pytest tests/ --cov=src --cov-report=term-missing
