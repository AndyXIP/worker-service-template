# Architecture

Request flow is a strict layering — routes are thin controllers, and each
layer only talks to the one directly below it:

```
api/routes  →  services  →  repositories  →  domain
   ↑                                           ↑
   └──────────── schemas (DTOs at the boundary) ┘
```

- **`domain/`** — framework-agnostic entities and domain exceptions (e.g.
  `NotFoundError`). No FastAPI or pydantic imports here.
- **`schemas/`** — pydantic request/response models. Only used at the API
  boundary; never passed into services/repositories as the internal type.
- **`repositories/`** — storage abstraction. `InMemoryItemRepository` is a
  `Protocol` implementation stored on `app.state` (reset per app instance, so
  fresh per test via the `client` fixture in `tests/conftest.py`). Swapping to
  a real database means writing a new class satisfying the same protocol —
  nothing above the repository layer changes.
- **`services/`** — business logic, orchestrates repositories.
- **`api/routes/`** — FastAPI routers; parse schema, call service, return schema.
- **`core/`** — cross-cutting infrastructure used by every layer, not part of
  the request-flow chain itself:
  - `config.py` — `pydantic-settings` `Settings`, cached via `get_settings()` (`lru_cache`).
  - `logging.py` — structlog setup; uvicorn's own logging is routed through
    the same JSON formatter, and `RequestLoggingMiddleware` emits one
    structured log line per request (method, path, status, duration).
    `/utils/health` is excluded from request logging (polled too frequently
    to be useful signal).
  - `errors.py` — exception handlers mapping validation errors, `NotFoundError`,
    `AuthenticationError`, and unhandled exceptions to one consistent JSON
    envelope: `{"error": {"type", "message", "details"}}`. No internals leak on 500s.
  - `auth.py` — **stubbed** bearer-token auth (`get_current_principal` /
    `Depends`). It only checks a token is present — it does not verify
    signature, expiry, or issuer, and accepts any non-empty token. Real
    verification (JWT check, IdP introspection, etc.) replaces `_authenticate`
    before this guards anything real. `items` writes (`POST`/`PATCH`/`DELETE`)
    require it; reads don't.

`main.py`'s `create_app()` is the composition root: builds `Settings`,
configures logging, registers exception handlers and middleware, wires the
in-memory repository onto `app.state`, and includes routers. CORS middleware
is only added if `CORS_ORIGINS` is non-empty.
