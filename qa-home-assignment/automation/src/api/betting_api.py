"""Thin HTTP client for the Sports Betting API.

Wraps the endpoints the tests touch and centralises auth (the ``x-user-id``
header). Each method returns the raw ``requests.Response`` so callers can read
``.status_code`` and ``.json()`` directly.
"""
from __future__ import annotations

from typing import Any

import requests


class BettingAPI:
    """Minimal client for the betting backend."""

    def __init__(self, base_url: str, user_id: str, timeout: int = 15) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        if user_id:
            self._session.headers.update({"x-user-id": user_id})
        self._session.headers.update({"Content-Type": "application/json"})

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def get_matches(self) -> requests.Response:
        return self._session.get(self._url("/api/matches"), timeout=self._timeout)

    def get_balance(self) -> requests.Response:
        return self._session.get(self._url("/api/balance"), timeout=self._timeout)

    def place_bet(self, match_id: str, selection: str, stake: Any) -> requests.Response:
        payload = {"matchId": match_id, "selection": selection, "stake": stake}
        return self._session.post(self._url("/api/place-bet"), json=payload, timeout=self._timeout)

    def reset_balance(self) -> requests.Response:
        return self._session.post(self._url("/api/reset-balance"), timeout=self._timeout)
