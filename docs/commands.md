# Commands

This project uses [mise](https://mise.jdx.dev/) as the task runner and
[uv](https://docs.astral.sh/uv/) for dependency management — do not invoke
`pytest`/`ruff`/`ty` directly if a `mise run` task covers it; use the task so
behavior matches CI.

```bash
mise run dev         # start the app with reload (http://127.0.0.1:8000, /docs for Swagger)
mise run test        # full suite: tests/unit + tests/integration, with coverage
mise run test-unit   # fast unit-only subset
mise run check       # ruff check + ruff format --check + ty typecheck (what CI runs)
mise run fix         # ruff check --fix + ruff format (also runs automatically as a pre-commit hook)
mise run typecheck   # ty check src/ only
mise run build       # docker build, tagged service-template:latest
```

Single test / single file:

```bash
pytest tests/unit/services/test_item.py
pytest tests/unit/services/test_item.py::test_create_item -v
```

`pythonpath = ["src"]` is set in `pyproject.toml`, so imports in `src/` and
tests are unqualified (e.g. `from core.config import get_settings`, not
`from src.core...`).

Entering the repo directory (mise's `enter` hook) auto-runs `uv sync --all-groups`
and installs pre-commit hooks (`fix` and [gitleaks](https://github.com/gitleaks/gitleaks)
on pre-commit, `typecheck` on pre-push). gitleaks scans staged changes for
hardcoded secrets; pre-commit manages its own Go toolchain to run it, so no
extra local install is needed.
