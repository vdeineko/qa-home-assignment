"""Page objects for the success and error modals."""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class SuccessReceipt(BasePage):
    ROOT = (By.ID, "modal-success")
    BET_ID = (By.ID, "modal-success-bet-id")
    MATCH = (By.ID, "modal-success-match")
    STAKE = (By.ID, "modal-success-stake")
    ODDS = (By.ID, "modal-success-odds")
    PAYOUT = (By.ID, "modal-success-payout")
    PLACED_AT = (By.ID, "modal-success-placed-at")
    CLOSE = (By.ID, "modal-success-close")

    def wait_visible(self) -> "SuccessReceipt":
        self.find_visible(self.ROOT)
        return self

    def bet_id(self) -> str:
        return self.text_of(self.BET_ID)

    def match(self) -> str:
        return self.text_of(self.MATCH)

    def stake(self) -> str:
        return self.text_of(self.STAKE)

    def odds(self) -> str:
        return self.text_of(self.ODDS)

    def payout(self) -> str:
        return self.text_of(self.PAYOUT)

    def placed_at(self) -> str:
        return self.text_of(self.PLACED_AT)

    def close(self) -> None:
        self.click(self.CLOSE)
        self._wait().until(EC.invisibility_of_element_located(self.ROOT))


class ErrorModal(BasePage):
    """Error modal (spec 2.5). Not used by the current tests; kept for failure-path tests."""

    ROOT = (By.ID, "modal-error")
    MESSAGE = (By.ID, "modal-error-message")
    REBET = (By.ID, "modal-error-rebet")
    CLOSE = (By.ID, "modal-error-close")
    CLOSE_X = (By.ID, "modal-error-close-x")

    def is_visible(self) -> bool:
        return self.is_present(self.ROOT)
