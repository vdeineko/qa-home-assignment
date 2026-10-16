"""Environment-driven configuration for the test suite.

Values are read from environment variables (optionally loaded from a local
``.env`` file). Nothing here is hard-coded to a candidate so the same code runs
locally and in CI.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

try:  # optional dependency; tests still run if python-dotenv is absent
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    """Immutable test configuration resolved from the environment."""

    base_url: str = os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app")
    user_id: str = os.getenv("USER_ID", "")
    headless: bool = _bool(os.getenv("HEADLESS"), True)
    timeout: int = int(os.getenv("TIMEOUT", "15"))

    @property
    def app_url(self) -> str:
        """Front-end URL with the user id attached as the auth query param."""
        return f"{self.base_url}/?user-id={self.user_id}"

    def require_user_id(self) -> str:
        """Return the user id or raise a clear error if it is missing."""
        if not self.user_id:
            raise RuntimeError(
                "USER_ID is not set. Export USER_ID=<your-issued-id> or add it "
                "to a .env file (see .env.example)."
            )
        return self.user_id


config = Config()
