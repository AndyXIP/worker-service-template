# Testing conventions

- `tests/unit/` mirrors `src/` layer-by-layer (isolated, no queue/dispatch loop running).
- `tests/integration/test_processing.py` drives the full stack through
  `consumers.dispatch.process_one` — publish a `Message` onto a real
  `InMemoryMessageQueue`, process exactly one message, assert the outcome
  (item persisted, or dead-lettered, or retried). `process_one` is split out
  from `run_forever` specifically so tests can drive one message at a time
  instead of running an infinite loop.
- `tests/integration/test_health.py` drives the health app through
  `TestClient` — the one remaining HTTP surface.
- The `queue`, `dead_letter_queue`, and `item_repository` fixtures
  (`tests/conftest.py`) are fresh per test — no state leaks between tests.
- Async test functions work without a `@pytest.mark.asyncio` decorator —
  `asyncio_mode = "auto"` is set in `pyproject.toml`.
- Coverage is enforced (`fail_under = 80` in `pyproject.toml`, `source = ["src"]`).
  `main()` itself is `# pragma: no cover` — it's an infinite loop wiring
  together the health server and dispatch loop, not meaningfully unit-testable;
  its two testable pieces (`build_handlers`, `_seed_sample_messages`) are
  covered directly in `tests/unit/test_main.py`.
