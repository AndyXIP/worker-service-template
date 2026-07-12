# Testing conventions

- `tests/unit/` mirrors `src/` layer-by-layer (isolated, no HTTP).
- `tests/integration/api/` drives the full stack through `TestClient`.
- The `client` fixture (`tests/conftest.py`) builds a fresh app per test via
  `create_app()`, so the in-memory item store never leaks between tests.
- The `auth_headers` fixture supplies a bearer token accepted by the auth stub
  (any non-empty token works — see `core/auth.py`).
- Coverage is enforced (`fail_under = 80` in `pyproject.toml`, `source = ["src"]`).
