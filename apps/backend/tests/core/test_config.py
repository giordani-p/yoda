import pytest
from pydantic import ValidationError

from app.core.config import DEV_AUTH_SECRET_KEY, Settings


def test_rejects_short_auth_secret_key() -> None:
    with pytest.raises(ValidationError, match="at least 32 characters"):
        Settings(auth_secret_key="short")


def test_rejects_dev_auth_secret_key_outside_development() -> None:
    with pytest.raises(ValidationError, match="outside the development environment"):
        Settings(app_env="production", auth_secret_key=DEV_AUTH_SECRET_KEY)


def test_accepts_custom_auth_secret_key_outside_development() -> None:
    settings = Settings(app_env="production", auth_secret_key="s" * 32)

    assert settings.auth_secret_key == "s" * 32
