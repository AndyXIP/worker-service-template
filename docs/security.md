# Security

## No inbound HTTP request surface

This is a worker: it has no inbound HTTP API to authenticate against or lock
down with CORS. The only HTTP surface is `health.py`'s `/utils/health`
liveness check, which is intentionally unauthenticated — it exists for
Docker `HEALTHCHECK`/k8s probes, not for clients, and carries no sensitive
data.

If your service needs to call *outbound* authenticated APIs (an identity
provider, another internal service, ...), that's a `services/`-layer
concern — wire credentials into the client you use there, rather than
reinventing an inbound-auth stub that doesn't apply to a worker.

## Message handling

`src/core/errors.py`'s `classify_error()` maps every handler exception to a
delivery outcome — `RETRY` or `DEAD_LETTER` — logged with a reason
(`not_found`, `validation_error`, `transient_error`,
`max_attempts_exceeded`). No stack trace or exception message is ever
forwarded into the dead-letter message itself, only into the structured log
line (`consumers/dispatch.py`) — keep that split if you extend the taxonomy,
so dead-lettered payloads don't end up carrying internal error detail
downstream.

## In-memory queue is not multi-tenant-safe

`InMemoryMessageQueue` and `InMemoryItemRepository` are single-process,
in-memory examples with no access control of their own — anything running in
the same process can publish/consume/read/write freely. That's fine for a
template; a real broker/database brings its own auth (IAM policy, connection
credentials, network policy) that should be configured before relying on
this in a shared environment.

## Reporting a vulnerability

See [`.github/SECURITY.md`](../.github/SECURITY.md) for how to report a
vulnerability in a service built from this template — this file covers the
security *posture* of the template itself, not the report-a-bug process.
