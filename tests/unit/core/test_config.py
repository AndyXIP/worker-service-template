import pytest

from core.config import Settings, get_settings


def test_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "worker-service-template"
    assert settings.environment == "local"
    assert settings.log_level == "INFO"
    assert settings.debug is False
    assert settings.port == 8000
    assert settings.max_delivery_attempts == 3


def test_reads_overrides_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_NAME", "my-service")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("MAX_DELIVERY_ATTEMPTS", "5")

    settings = Settings(_env_file=None)

    assert settings.app_name == "my-service"
    assert settings.environment == "production"
    assert settings.log_level == "DEBUG"
    assert settings.port == 9000
    assert settings.max_delivery_attempts == 5


def test_get_settings_is_cached() -> None:
    get_settings.cache_clear()

    assert get_settings() is get_settings()

    get_settings.cache_clear()
