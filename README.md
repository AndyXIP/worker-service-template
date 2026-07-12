# worker-service-template

![Status](https://img.shields.io/badge/Status-Template-blue) ![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.139+-009688?logo=fastapi&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-2-E92063?logo=pydantic&logoColor=white) ![structlog](https://img.shields.io/badge/structlog-JSON%20logging-black) ![License](https://img.shields.io/badge/License-MIT-green)

A message/task-queue worker service template — async processing off the
request path, triggered by messages rather than HTTP calls. Clone it, delete
the example `item` message processor, and build your actual worker in its
place — the surrounding structure (config, structured logging, retry/dead-
letter handling, layered architecture, tests, CI, Docker) is meant to be
copied as-is.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development Notes](#development-notes)
- [Suggested Future Directions](#suggested-future-directions)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

This is a starting point for a new worker service, not a finished product.
The `item` message processor in `src/` is a worked example — consuming
`item.create`/`item.delete` messages, layered architecture, validation,
retry/dead-letter handling, and tests — that exists purely to demonstrate the
patterns a new message type in your real service should follow. Everything
around it (Docker, CI, pre-commit, task runner) is already production-
flavored and untouched by the example.

This is a **message/task-queue consumer** pattern (a competing-consumers
worker pulling discrete work items off a queue), not strict pub/sub
event-driven architecture (past-tense facts fanned out to independent
subscribers) — the far more common shape for "async processing off the
request path" in practice.

---

## Features

- **Layered architecture** — domain entities, message schemas, repositories,
  and services are cleanly separated; consumers stay thin handlers.
- **Typed configuration** — `pydantic-settings` reads env vars / `.env`,
  validated at startup.
- **Structured JSON logging** — `structlog`, one structured log line per
  message processed (id, type, attempt, outcome, duration).
- **Retry + dead-letter handling** — `core/errors.py` classifies handler
  failures into retry (transient) or dead-letter (permanent, e.g.
  not-found/validation) outcomes, with a configurable attempt ceiling.
- **Full example message processor** — `item.create`/`item.delete`, with
  success, dead-letter, and retry-then-dead-letter paths to copy from.
- **Real test suite** — unit tests per layer plus integration tests that
  drive messages through the full dispatch loop.
- **Minimal health surface** — a single `/utils/health` endpoint (the only
  HTTP in the whole service) so Docker `HEALTHCHECK`/k8s probes still work.
- **Production-flavored Docker/CI** — multi-stage build, non-root user,
  `HEALTHCHECK`, and a GitHub Actions pipeline that lints, type-checks,
  tests, Trivy-scans, and smoke-tests the built image.
- **Secret scanning** — [gitleaks](https://github.com/gitleaks/gitleaks) runs
  as a pre-commit hook, catching hardcoded credentials before they're committed.

---

## Architecture

```
┌───────────────────────────┐
│  Message queue            │  in-memory example; swap for a real broker
└────────────┬──────────────┘
             │  Message
             ▼
┌───────────────────────────┐
│  consumers                │  dispatch loop: ack / retry / dead-letter
├───────────────────────────┤
│  services                 │  business logic, orchestrates repositories
├───────────────────────────┤
│  repositories             │  storage abstraction (in-memory for this template)
├───────────────────────────┤
│  domain                   │  entities + domain exceptions, framework-agnostic
└───────────────────────────┘
             ▲
             │  DTOs at the boundary only
      schemas (pydantic message payload models)
```

`core/` (`config`, `logging`, `queue`, `errors`) is cross-cutting
infrastructure used by every layer above, not part of the processing-flow
chain itself. `health.py` is a minimal FastAPI app with just
`/utils/health` — the only inbound HTTP in the service.

See [docs/architecture.md](docs/architecture.md) for a deeper breakdown of
each layer's responsibilities, and how local dev seeds demo messages since
there's no HTTP endpoint to curl.

---

## Tech Stack

- **asyncio** — the dispatch loop and in-memory queue
- **FastAPI** + **Uvicorn** — used only for the minimal `/utils/health` surface
- **Pydantic v2 / pydantic-settings** — validation and typed settings
- **structlog** — structured JSON logging
- **uv** — Python package manager
- **mise** — dev tool + task runner (Python, uv, lint/test/build tasks)
- **Ruff** — linter and formatter
- **ty** — type checker
- **pytest** / **pytest-asyncio** — test runner

---

## Project Structure

```
worker-service-template/
├── .github/
│   ├── workflows/             # CI: lint+typecheck+test+build+smoke test (deploy.yml wired, no-op)
│   ├── actions/mise-install/  # composite action: install mise + toolchain, uv sync
│   ├── ISSUE_TEMPLATE/        # bug report + feature request forms
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS             # placeholder — replace before enabling required reviews
│   └── SECURITY.md            # placeholder — how to report a vulnerability
├── .claude/settings.json      # Claude Code permissions allowlist (project-shared, not personal)
├── .mise/
│   ├── config.toml            # pinned Python/uv versions, `enter` hook (uv sync + pre-commit install)
│   └── tasks/                 # dev, check, fix, test, test-unit, typecheck, build
├── docs/                      # detail linked from CLAUDE.md: architecture, commands, testing, ci, security
├── src/
│   ├── main.py                # worker entrypoint + composition root
│   ├── health.py              # minimal FastAPI app: /utils/health only
│   ├── core/
│   │   ├── config.py          # pydantic-settings Settings
│   │   ├── logging.py         # structlog config
│   │   ├── queue.py           # Message + MessageQueue protocol + InMemoryMessageQueue
│   │   └── errors.py          # classify_error: exception -> retry/dead-letter outcome
│   ├── domain/                # entities + domain exceptions (framework-agnostic)
│   ├── schemas/               # pydantic message payload DTOs
│   ├── repositories/          # storage abstraction (in-memory here)
│   ├── services/              # business logic, orchestrates repositories
│   └── consumers/             # message handlers + the dispatch loop
├── tests/
│   ├── unit/                  # fast, isolated per-layer tests
│   └── integration/           # dispatch loop (test_processing.py) + health app (test_health.py)
├── CLAUDE.md                  # guidance for Claude Code / agents (short, links into docs/)
├── .env.example               # documents Settings fields
├── Dockerfile                 # multi-stage, non-root, HEALTHCHECK
├── .pre-commit-config.yaml
├── pyproject.toml
└── uv.lock
```

---

## Getting Started

**Prerequisite:** [mise](https://mise.jdx.dev/) — see its site for install instructions for your platform.

`cd` into the repo — mise's `enter` hook auto-runs `uv sync` and installs the
pre-commit hooks. Then:

```bash
mise run dev
```

The worker starts consuming its seeded demo messages immediately — watch the
structured logs. The health check is available at
`http://127.0.0.1:8000/utils/health`.

---

## Configuration

All configuration is loaded from environment variables via `pydantic-settings`
(`src/core/config.py`). See `.env.example` for a ready-to-copy template — all
fields have defaults, so `.env` is optional.

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `worker-service-template` | Used in the startup log |
| `ENVIRONMENT` | `local` | One of `local`, `staging`, `production`. `local` also seeds demo messages at startup |
| `LOG_LEVEL` | `INFO` | Standard Python log level name |
| `DEBUG` | `false` | Reserved for local debugging toggles |
| `PORT` | `8000` | Health server bind port |
| `MAX_DELIVERY_ATTEMPTS` | `3` | Attempts before a failing message is dead-lettered |

---

## Usage

There's no HTTP API to call — the worker consumes messages published onto
its `MessageQueue`. The two example message types:

| Type | Payload | Outcome |
|---|---|---|
| `item.create` | `{"name", "description"?, "price"}` | Creates an item |
| `item.delete` | `{"item_id"}` | Deletes an item — dead-lettered if the id doesn't exist |

```python
from core.queue import Message

await queue.publish(
    Message(type="item.create", payload={"name": "Widget", "price": 9.99})
)
await queue.publish(Message(type="item.delete", payload={"item_id": str(some_id)}))
```

In local dev, `main.py` seeds one of each automatically so `mise run dev` has
something to process out of the box (see
[Development Notes](#development-notes)). In tests, publish directly onto a
queue fixture and drive it with `consumers.dispatch.process_one` — see
[docs/testing.md](docs/testing.md).

---

## Development Notes

- **In-memory only**: both the queue and the `item` store are in-memory,
  reset on every restart (and fresh per test) — no broker or database is
  wired up on purpose, so the template stays unopinionated about which
  one you'll use.
- **Swap the queue and the repository, not the dispatch loop**:
  `InMemoryMessageQueue` (`src/core/queue.py`) implements `MessageQueue`;
  `InMemoryItemRepository` (`src/repositories/item.py`) implements
  `ItemRepository`. Replace either with a real implementation and nothing
  above that layer needs to change.
- **No way to publish into a running process from outside it**: that's a
  known limitation of the in-memory queue example, not a bug — see
  [docs/architecture.md](docs/architecture.md#the-how-do-i-trigger-it-locally-gap).
  Swapping in a real broker is what makes cross-process publishing possible.
- **Retry/dead-letter**: every handler failure — not-found, validation, or
  unexpected — resolves to either a retry (requeued with `attempt`
  incremented) or a dead-letter, via `core/errors.py`'s `classify_error`.
- **No `--reload` in dev**: the worker is a long-running dispatch loop, not
  an ASGI app uvicorn can hot-reload the way an API server can.
- **CI pipeline**: pushes and PRs run `mise run check` (lint + typecheck),
  `mise run test`, and `mise run build` (Docker build + health-check smoke
  test) via GitHub Actions — see [docs/ci.md](docs/ci.md) for the full breakdown.
- **Port is runtime-configurable**: the health server binds `$PORT` if set,
  else `8000` — works unmodified whether a platform injects its own port
  (Railway, Render) or expects a fixed one (AWS ECS/Fargate).
- **CODEOWNERS is a placeholder**: `.github/CODEOWNERS` has a `@your-org/your-team`
  stub — GitHub can't auto-populate this from template metadata, so replace it
  with real owners and enable "Require review from Code Owners" in branch
  protection settings before it does anything.
- **SECURITY.md is a placeholder**: `.github/SECURITY.md` has a stub contact
  email — replace it with a real address, or switch to GitHub's private
  vulnerability reporting instead.

```bash
mise run test         # full suite (tests/unit + tests/integration)
mise run test-unit    # fast unit-only subset
mise run check        # ruff + ty
```

---

## Suggested Future Directions

Things intentionally left out of the template — add them once your service
actually needs them:

- A real broker (swap `InMemoryMessageQueue` for an SQS/Redis Streams/RabbitMQ-backed one)
- A real persistence layer (swap `InMemoryItemRepository` for a SQL/Mongo-backed one)
- Graceful shutdown / in-flight message draining on `SIGTERM`
- Idempotency keys, if the real broker can redeliver a message more than once
- Metrics on queue depth, dead-letter volume, and processing latency
- Dev-mode autoreload (e.g. `watchfiles python -m main`) if hot-reload during
  development is worth the added dependency
- Dependabot (or Renovate) to keep dependencies and pinned Actions/tool versions current
- A real deploy step — `deploy.yml` is already wired up (auto-deploys to a
  `development` Environment after CI passes on `main`; `production` deploys via a
  manual `workflow_dispatch` run) but both `Deploy` steps are no-op placeholders

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — the minimal health-check surface
- [Pydantic](https://docs.pydantic.dev/) — validation and settings
- [structlog](https://www.structlog.org/) — structured logging
- [uv](https://docs.astral.sh/uv/) — package manager
- [mise](https://mise.jdx.dev/) — dev tool and task runner
- [Ruff](https://docs.astral.sh/ruff/) — linter and formatter
