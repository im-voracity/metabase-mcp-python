"""Custom exception hierarchy for Metabase API errors."""


class MetabaseError(Exception):
    """Base exception for Metabase API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {super().__str__()}"
        return super().__str__()


class MetabaseAuthError(MetabaseError):
    """Authentication or authorization failed (401/403)."""


class MetabaseNotFoundError(MetabaseError):
    """Resource not found (404)."""


class MetabaseAPIError(MetabaseError):
    """General API error (other 4xx/5xx)."""
