"""Base page object with shared Selenium helpers (explicit waits only)."""
from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.timeout = timeout

    def _wait(self) -> WebDriverWait:
        return WebDriverWait(self.driver, self.timeout)

    def find_visible(self, locator: tuple[str, str]) -> WebElement:
        return self._wait().until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator: tuple[str, str]) -> WebElement:
        return self._wait().until(EC.element_to_be_clickable(locator))

    def click(self, locator: tuple[str, str]) -> None:
        self.find_clickable(locator).click()

    def text_of(self, locator: tuple[str, str]) -> str:
        return self.find_visible(locator).text.strip()

    def is_present(self, locator: tuple[str, str]) -> bool:
        return bool(self.driver.find_elements(*locator))
