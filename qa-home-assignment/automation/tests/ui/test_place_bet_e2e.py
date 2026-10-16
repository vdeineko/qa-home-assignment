"""End-to-end UI test for the critical bet-placement journey.

Why this was chosen for automation
----------------------------------
Placing a bet is the core revenue journey: the user commits money, and the UI,
client state and backend must agree. This test covers the integration seam that
API tests cannot (odds button -> bet slip -> place-bet -> receipt -> balance).

Expected values come from live ``/api/matches`` data and the starting balance is
read at runtime, never assumed (reset-balance is unreliable, see BUG-06).
"""
from __future__ import annotations

import pytest
from pytest import approx

from src.pages.bet_slip import BetSlip
from src.pages.receipt_modal import SuccessReceipt
from src.utils import parse_amount

STAKE = 5.00
SELECTION = "HOME"


@pytest.mark.ui
@pytest.mark.smoke
def test_place_bet_happy_path(open_app, driver, config, api, upcoming_match):
    """Select odds, enter stake, place the bet; stake is deducted and slip is cleared."""
    expected_odds = upcoming_match["odds"]["home"]
    expected_payout = round(STAKE * expected_odds, 2)
    balance_before = api.get_balance().json()["balance"]

    # The odds button shows the catalogue price.
    assert open_app.odds_value(upcoming_match["id"], SELECTION) == approx(expected_odds)

    open_app.select_outcome(upcoming_match["id"], SELECTION)
    slip = BetSlip(driver, config.timeout).wait_loaded()
    assert slip.selection_count() == 1

    slip.enter_stake(STAKE)
    assert parse_amount(slip.potential_payout_text()) == approx(expected_payout, abs=0.01)

    slip.place_bet()

    receipt = SuccessReceipt(driver, config.timeout).wait_visible()
    assert receipt.bet_id(), "receipt is missing a bet id"
    assert receipt.placed_at(), "receipt is missing a placement timestamp"
    assert parse_amount(receipt.stake()) == approx(STAKE, abs=0.01)
    assert parse_amount(receipt.odds()) == approx(expected_odds, abs=0.01)
    receipt_payout = parse_amount(receipt.payout())
    # Next step is failing because of BUG-01
    assert receipt_payout == approx(expected_payout, abs=0.01), (
        f"receipt payout {receipt_payout} != stake x odds {expected_payout}"
    )

    # Spec 2.3: on success the stake is deducted. Checked at the source of truth
    # (API); the header display is a known defect (BUG-08).
    balance_after = api.get_balance().json()["balance"]
    assert balance_after == approx(balance_before - STAKE, abs=0.01)

    # Spec 2.4: closing the receipt returns to the main flow with no active selection.
    receipt.close()
    assert not slip.has_active_selection(), "selection still active after closing receipt"
