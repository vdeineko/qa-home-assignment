"""Root pytest fixtures: configuration, API client and Selenium WebDriver."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.api.betting_api import BettingAPI
from src.config import config as _config
from src.pages.match_list_page import MatchListPage


@pytest.fixture(scope="session")
def config():
    return _config


@pytest.fixture()
def api(config) -> BettingAPI:
    """Authenticated API client. Fails fast if USER_ID is not configured."""
    config.require_user_id()
    return BettingAPI(config.base_url, config.user_id, config.timeout)


@pytest.fixture()
def reset_balance_around_test(api):
    """Reset the balance before the test (enough funds) and after it (clean state).

    Tests must not assume the exact post-reset value: the reset endpoint is known
    to persist a value different from the one it returns (see bug_reports.md, BUG-06).
    """
    response = api.reset_balance()
    assert response.status_code == 200, f"reset-balance failed: {response.status_code}"
    yield
    api.reset_balance()


@pytest.fixture()
def upcoming_match(api) -> dict:
    """First match with kickoff today or later (spec: upcoming matches only, see BUG-03)."""
    response = api.get_matches()
    assert response.status_code == 200, f"could not load matches: {response.status_code}"
    today = datetime.now(timezone.utc).date().isoformat()
    upcoming = [match for match in response.json() if match["kickoffDate"] >= today]
    assert upcoming, "no upcoming matches in the catalogue"
    return upcoming[0]


@pytest.fixture()
def driver(config):
    """Chrome WebDriver. Selenium Manager auto-resolves the matching driver."""
    config.require_user_id()
    options = Options()
    if config.headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,900")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture()
def open_app(reset_balance_around_test, driver, config) -> MatchListPage:
    """Navigate to the authenticated app and return a loaded MatchListPage."""
    driver.get(config.app_url)
    return MatchListPage(driver, config.timeout).wait_loaded()


ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save a screenshot when a UI test fails (unexpected failures only, not xfails)."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed or hasattr(report, "wasxfail"):
        return
    driver = item.funcargs.get("driver")
    if driver is None:
        return
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    path = ARTIFACTS_DIR / f"{item.name}.png"
    driver.save_screenshot(str(path))
    report.sections.append(("screenshot", str(path)))
