"""Page object for the match list / betting board (incl. header balance)."""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from ..utils import parse_amount
from .base_page import BasePage

SELECTIONS = {"HOME": "home", "DRAW": "draw", "AWAY": "away"}


class MatchListPage(BasePage):
    MATCH_LIST = (By.ID, "match-list")
    # The pill holds an icon ligature span plus a "Balance: €x.xx" span; target the text span.
    HEADER_BALANCE_AMOUNT = (By.CSS_SELECTOR, "#header-balance > span:not(.icon)")

    def wait_loaded(self) -> "MatchListPage":
        self.find_visible(self.MATCH_LIST)
        return self

    def balance(self) -> float:
        """Current balance shown in the header, as a number."""
        return parse_amount(self.text_of(self.HEADER_BALANCE_AMOUNT))

    def wait_balance_equals(self, expected: float, timeout: float | None = None) -> float:
        """Wait until the header balance updates to the expected value."""
        WebDriverWait(self.driver, timeout or self.timeout).until(
            lambda _: abs(self.balance() - expected) < 0.005
        )
        return self.balance()

    def _odds_locator(self, match_id: str, selection: str) -> tuple[str, str]:
        return (By.ID, f"odds-{match_id}-{SELECTIONS[selection.upper()]}")

    def select_outcome(self, match_id: str, selection: str) -> "MatchListPage":
        """Click an odds button (1/X/2) for the given match and selection."""
        self.click(self._odds_locator(match_id, selection))
        return self

    def odds_value(self, match_id: str, selection: str) -> float:
        """Odds shown on the button (the button also renders a '1'/'X'/'2' label span)."""
        button = self.find_visible(self._odds_locator(match_id, selection))
        return parse_amount(button.find_element(By.CSS_SELECTOR, ".oddsButtonValue").text)
