"""API-layer test: a stake above the available balance is rejected.

Why this test was chosen for automation
---------------------------------------
"Stake must not exceed available balance" is a money rule the spec puts on both
layers (4.1, "UI + API"). The UI blocks it, so only a direct API call shows
whether the backend enforces it. If it does not, a user can bet money they do not
have and the balance goes negative. It runs in seconds, without a browser.

Pre-step: reset the balance, then place one bet so the balance drops below the
€100 per-bet maximum. Only then can a valid stake exceed the balance.
Post-step: ``reset_balance_around_test`` resets the balance again.
"""
from __future__ import annotations

import pytest
from pytest import approx

TARGET_BALANCE = 50.00  # well below the €100 per-bet maximum


@pytest.fixture()
def balance_below_max_stake(api, reset_balance_around_test, upcoming_match) -> float:
    """Place one bet so the balance drops to TARGET_BALANCE; return the new balance."""
    balance = api.get_balance().json()["balance"]
    drain_stake = round(balance - TARGET_BALANCE, 2)
    response = api.place_bet(upcoming_match["id"], "HOME", drain_stake)
    assert response.status_code == 200, f"pre-step bet failed: {response.status_code}"
    return api.get_balance().json()["balance"]


@pytest.mark.api
@pytest.mark.xfail(
    reason="Known defect BUG-02: API accepts a stake above the balance",
    raises=AssertionError,
)
def test_stake_above_balance_is_rejected(api, upcoming_match, balance_below_max_stake):
    """A stake €1 above the balance is rejected with 422 and the balance is unchanged."""
    stake = round(balance_below_max_stake + 1, 2)

    response = api.place_bet(upcoming_match["id"], "HOME", stake)

    # Next step is failing because of BUG-02
    assert response.status_code == 422, (
        f"expected 422 for stake {stake} with balance {balance_below_max_stake}, "
        f"got {response.status_code}: {response.text}"
    )
    assert response.json()["error"] == "insufficient_balance", response.text
    assert api.get_balance().json()["balance"] == approx(balance_below_max_stake)
