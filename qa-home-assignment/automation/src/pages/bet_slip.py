"""Page object for the right-hand bet slip panel."""
from __future__ import annotations

from selenium.webdriver.common.by import By

from .base_page import BasePage


class BetSlip(BasePage):
    ROOT = (By.ID, "bet-slip")
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    PLACE_BET = (By.ID, "bet-slip-place-bet")
    REMOVE_ALL = (By.ID, "bet-slip-remove-all")
    SELECTION_REMOVE = (By.ID, "bet-slip-selection-remove")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    TOTAL_STAKE = (By.ID, "bet-slip-total-stake")
    COUNT = (By.ID, "bet-slip-count")

    def wait_loaded(self) -> "BetSlip":
        self.find_visible(self.ROOT)
        return self

    def enter_stake(self, stake: str | float) -> "BetSlip":
        field = self.find_visible(self.STAKE_INPUT)
        field.clear()
        field.send_keys(str(stake))
        return self

    def potential_payout_text(self) -> str:
        return self.text_of(self.POTENTIAL_PAYOUT)

    def selection_count(self) -> int:
        return int(self.text_of(self.COUNT))

    def has_active_selection(self) -> bool:
        """The stake input is only rendered while a selection is in the slip."""
        return self.is_present(self.STAKE_INPUT)

    def place_bet(self) -> None:
        self.click(self.PLACE_BET)

    def remove_all(self) -> None:
        self.click(self.REMOVE_ALL)
