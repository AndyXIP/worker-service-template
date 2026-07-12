# Security

## Auth

`src/core/auth.py` is a **stub**, not real security. `get_current_principal`
(wired via `Depends`) only checks that a bearer token is present — it does
not verify a signature, expiry, or issuer, and accepts any non-empty token.
It exists to demonstrate the wiring pattern (`Depends` on a route, a 401
`AuthenticationError` → standard error envelope on failure) so every service
doesn't reinvent that plumbing independently.

Replace `_authenticate` with real verification (JWT signature/expiry check,
an introspection call to your identity provider, etc.) before relying on it
for anything that matters. The example `items` writes (`POST`/`PATCH`/
`DELETE`) require it; reads don't — adjust that split to your service's needs.

`Principal` (also in `auth.py`) is the authenticated caller; it currently
carries only the raw token. Extend it once real verification yields more
(user id, scopes, roles) — routes and services should depend on `Principal`,
never parse the raw token themselves.

## CORS

CORS middleware (`src/main.py`) is only added if `CORS_ORIGINS` (see
`src/core/config.py`) is non-empty — no origins configured means no
cross-origin access at all. When you do set origins:

- `allow_credentials=True` means the browser will send cookies/auth headers
  on cross-origin requests from those origins.
- `allow_methods`/`allow_headers` are scoped to what this service actually
  needs, not wildcarded. Combining `allow_credentials=True` with a `"*"`
  wildcard on origins/methods/headers is a common footgun once real auth is
  wired in — widen only when a specific method or header is genuinely required.

## Error responses

`src/core/errors.py` maps every error — validation, not-found, auth, or
unhandled — to one consistent envelope (`{"error": {"type", "message",
"details"}}`) and no internals leak on 500s (no stack trace, no exception
message from unhandled exceptions).

## Reporting a vulnerability

See [`.github/SECURITY.md`](../.github/SECURITY.md) for how to report a
vulnerability in a service built from this template — this file covers the
security *posture* of the template itself, not the report-a-bug process.
