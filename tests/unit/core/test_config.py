import pytest

from core.config import Settings


def test_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "service-template"
    assert settings.environment == "local"
    assert settings.log_level == "INFO"
    assert settings.cors_origins == []
    assert settings.debug is False


def test_reads_overrides_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_NAME", "my-service")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings(_env_file=None)

    assert settings.app_name == "my-service"
    assert settings.environment == "production"
    assert settings.log_level == "DEBUG"
