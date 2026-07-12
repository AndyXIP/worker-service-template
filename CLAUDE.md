# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A message/task-queue worker service template, not a finished product —
async processing off the request path, triggered by messages rather than
HTTP calls. The `item` message processor under `src/` is a worked example
(consuming `item.create`/`item.delete`, layered architecture, validation,
retry/dead-letter handling, tests) that exists purely to demonstrate the
patterns a new message type should follow. When adapting this template into
a real service, the `item` processor is deleted and replaced — everything
else (Docker, CI, pre-commit, task runner, `core/`) is meant to be copied
as-is.

## Commands

`mise run check` (lint + format-check + typecheck) and `mise run test` (full
suite) are what CI runs — use these, not raw `pytest`/`ruff`/`ty`, so local
results match CI. See [docs/commands.md](docs/commands.md) for the full task
list and single-test invocation.

## Architecture

Strict layering — consumers are thin handlers, schemas are message-payload
DTOs at the boundary only, and each layer talks solely to the one below it:
`consumers → services → repositories → domain`. `core/` holds cross-cutting
infrastructure (config, logging, queue, errors) used by every layer. There's
no inbound HTTP API — `health.py` is a minimal `/utils/health` surface for
Docker/k8s probes only. See [docs/architecture.md](docs/architecture.md) for
the full breakdown of each layer's responsibilities.

## Testing conventions

Unit tests mirror `src/` layer-by-layer; integration tests drive the full
dispatch loop via `consumers.dispatch.process_one`. See
[docs/testing.md](docs/testing.md) for fixture details and coverage requirements.

## CI

Push and PR both run lint/typecheck, tests, and a Docker build + smoke test.
See [docs/ci.md](docs/ci.md) for the workflow breakdown and `deploy.yml`'s status.

## Security

There's no inbound HTTP request surface to authenticate or CORS-protect —
only the unauthenticated `/utils/health` check. See
[docs/security.md](docs/security.md) for the retry/dead-letter error
taxonomy and the in-memory queue/repository's limitations.
