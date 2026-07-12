# Architecture

This is a message/task-queue consumer (competing-consumers worker pulling
discrete work items off a queue) - not strict pub/sub event-driven
architecture (past-tense facts fanned out to independent subscribers). The
processing flow is a strict layering, each layer only talking to the one
directly below it:

```
consumers  →  services  →  repositories  →  domain
   ↑                                          ↑
   └──────────── schemas (message payload DTOs) ┘
```

- **`domain/`** — framework-agnostic entities and domain exceptions (e.g.
  `NotFoundError`). No FastAPI, pydantic-at-the-boundary, or queue imports here.
- **`schemas/`** — pydantic message payload models (`ItemCreatePayload`,
  `ItemDeletePayload`). Only used at the message boundary; never passed into
  services/repositories as the internal type.
- **`repositories/`** — storage abstraction. `InMemoryItemRepository` is a
  `Protocol` implementation constructed once in `main.py`'s composition root
  (fresh per test via the `item_repository` fixture in `tests/conftest.py`).
  Swapping to a real database means writing a new class satisfying the same
  protocol — nothing above the repository layer changes.
- **`services/`** — business logic, orchestrates repositories.
- **`consumers/`** — one handler per message type (`consumers/item.py`), plus
  the generic dispatch loop (`consumers/dispatch.py`) that pulls a `Message`
  off the queue, looks up its handler by `message.type`, and classifies the
  outcome (ack / retry / dead-letter).
- **`core/`** — cross-cutting infrastructure used by every layer, not part of
  the processing-flow chain itself:
  - `config.py` — `pydantic-settings` `Settings`, cached via `get_settings()`
    (`lru_cache`). Includes `port` (health server bind port) and
    `max_delivery_attempts` (retry/dead-letter threshold).
  - `logging.py` — structlog setup; uvicorn's own logging (used only by the
    health server) is routed through the same JSON formatter. The dispatch
    loop emits one structured log line per message (id, type, attempt,
    outcome, duration) — the message-shaped analog of a per-request log line.
  - `queue.py` — `Message` (id, type, payload, attempt), the `MessageQueue`
    Protocol (`publish`/`get`), and `InMemoryMessageQueue` (`asyncio.Queue`-
    backed). Swapping to SQS/Redis Streams/RabbitMQ means writing one new
    class satisfying the Protocol — nothing above it changes, exactly like
    the repository story.
  - `errors.py` — `classify_error(exc, attempt, max_attempts)` maps a handler
    exception to a `DeliveryOutcome` (`RETRY` or `DEAD_LETTER`) plus a short
    reason for logging. `NotFoundError` and payload validation errors are
    permanent business failures and go straight to dead-letter; anything
    else retries up to `max_delivery_attempts` before being dead-lettered too.

`health.py`'s `create_health_app()` is a minimal FastAPI app with just
`/utils/health` — not a layer, just the HTTP surface Docker `HEALTHCHECK`/k8s
probes hit, since the worker itself has no inbound HTTP.

`main.py` is the composition root: builds `Settings`, configures logging,
constructs the queue/dead-letter-queue/repository/service, builds the handler
registry (`build_handlers`), seeds a couple of demo messages in the `local`
environment (see below), and runs the health server and the dispatch loop
concurrently via `asyncio.TaskGroup`.

## The "how do I trigger it locally" gap

An in-memory queue is process-local: nothing outside the running process can
publish into it (there's no HTTP endpoint that accepts messages — that's the
point of processing happening off the request path). So `mise run dev` has
nothing to consume unless something seeds it. `main.py`'s
`_seed_sample_messages()` publishes one `item.create` (succeeds) and one
`item.delete` for a nonexistent id (demonstrates the dead-letter path) when
`ENVIRONMENT=local`, standing in for whatever a real producer/upstream
service would publish. It's demo-only scaffolding — delete it once a real
`MessageQueue` implementation replaces `InMemoryMessageQueue`, since a real
broker is what makes cross-process publishing possible in the first place.
Integration tests don't rely on this seeding; they publish directly to a
queue instance they construct.
