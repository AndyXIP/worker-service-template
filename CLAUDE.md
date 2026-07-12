# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A FastAPI backend service template, not a finished product. The `items` resource
under `src/` is a worked example (full CRUD, layered architecture, validation,
error handling, tests) that exists purely to demonstrate the patterns a new
resource should follow. When adapting this template into a real service, the
`items` resource is deleted and replaced — everything else (Docker, CI,
pre-commit, task runner, `core/`) is meant to be copied as-is.

## Commands

`mise run check` (lint + format-check + typecheck) and `mise run test` (full
suite) are what CI runs — use these, not raw `pytest`/`ruff`/`ty`, so local
results match CI. See [docs/commands.md](docs/commands.md) for the full task
list and single-test invocation.

## Architecture

Strict layering — routes are thin controllers, schemas are DTOs at the API
boundary only, and each layer talks solely to the one below it:
`api/routes → services → repositories → domain`. `core/` holds cross-cutting
infrastructure (config, logging, errors, auth) used by every layer.
See [docs/architecture.md](docs/architecture.md) for the full breakdown of
each layer's responsibilities.

## Testing conventions

Unit tests mirror `src/` layer-by-layer; integration tests drive the full
stack through `TestClient`. See [docs/testing.md](docs/testing.md) for
fixture details and coverage requirements.

## CI

Push and PR both run lint/typecheck, tests, and a Docker build + smoke test.
See [docs/ci.md](docs/ci.md) for the workflow breakdown and `deploy.yml`'s status.

## Security

Auth (`src/core/auth.py`) is a stub — presence-only bearer token check, no
signature/expiry verification. CORS is opt-in via `CORS_ORIGINS`. See
[docs/security.md](docs/security.md) for what's stubbed, what to replace
before relying on it, and CORS footguns to avoid.
