"""Независимые фикстуры браузера и HTTP-клиента."""

import os
from collections.abc import Generator

import allure
import pytest
from api.kinopoisk_client import ApiSettings, KinopoiskApiClient
from config.loader import load_config
from playwright.sync_api import Page, expect, sync_playwright
from pytest import CallInfo, Config, Item, Parser, TestReport


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: Item,
    call: CallInfo[None],
) -> Generator[None, object, None]:
    """Сохранить результат фазы для вложений UI при падении."""
    outcome = yield
    report: TestReport = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def pytest_addoption(parser: Parser) -> None:
    """Добавить переключатель видимого браузера."""
    parser.addoption("--headed",
                     action="store_true", help="Показать Chromium")


@pytest.fixture()
def page(
    request: pytest.FixtureRequest, pytestconfig: Config
) -> Generator[Page, None, None]:
    """Новый браузерный контекст на тест; никаких общих cookies."""
    ui = load_config("settings.json")["ui"]
    headless = not pytestconfig.getoption("--headed")
    if os.getenv("KINOPOISK_HEADLESS", "").lower() == "false":
        headless = False
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(viewport=ui["viewport"])
        context.set_default_timeout(ui["timeout_ms"])
        context.set_default_navigation_timeout(ui["navigation_timeout_ms"])
        expect.set_options(timeout=ui["timeout_ms"])
        test_page = context.new_page()
        try:
            yield test_page
        finally:
            report = getattr(request.node, "rep_call", None)
            if (
                report is not None
                and report.failed
                and not test_page.is_closed()
            ):
                try:
                    allure.attach(
                        test_page.screenshot(timeout=5000),
                        name="Страница при ошибке",
                        attachment_type=allure.attachment_type.PNG,
                    )
                except Exception as error:
                    allure.attach(
                        type(error).__name__,
                        name="Скриншот недоступен",
                        attachment_type=allure.attachment_type.TEXT,
                    )
            context.close()
            browser.close()


@pytest.fixture()
def api_settings() -> ApiSettings:
    """Настройки без выполнения сетевых запросов."""
    return ApiSettings.from_environment()


@pytest.fixture()
def api_client(
    api_settings: ApiSettings,
) -> Generator[KinopoiskApiClient, None, None]:
    """Нет токена — ошибка настройки, а не ложный успешный прогон."""
    if not api_settings.token:
        pytest.fail("Не задан KINOPOISK_API_TOKEN", pytrace=False)
    client = KinopoiskApiClient(api_settings)
    try:
        yield client
    finally:
        client.close()
