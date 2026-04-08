"""Configuration management via environment variables.

Loads METABASE_URL, METABASE_API_KEY, METABASE_USERNAME, METABASE_PASSWORD
from environment variables or .env file.
"""

from typing import Self
from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MetabaseConfig(BaseSettings):
    """Metabase connection configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="METABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str
    api_key: str | None = None
    username: str | None = None
    password: str | None = None

    @model_validator(mode="after")
    def validate_auth_and_url(self) -> Self:
        # Validate URL
        parsed = urlparse(self.url)
        if not parsed.scheme or not parsed.netloc:
            msg = f"Invalid Metabase URL: {self.url!r}. Must be a valid URL (e.g. http://localhost:3000)"
            raise ValueError(msg)

        # Validate auth: need api_key OR (username AND password)
        has_api_key = bool(self.api_key)
        has_credentials = bool(self.username) and bool(self.password)

        if not has_api_key and not has_credentials:
            msg = (
                "Metabase authentication not configured. "
                "Provide METABASE_API_KEY or both METABASE_USERNAME and METABASE_PASSWORD."
            )
            raise ValueError(msg)

        return self
