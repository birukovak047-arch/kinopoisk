"""Page Object карточки фильма."""

import re
from urllib.parse import urljoin

from allure import step
from config.loader import load_config
from playwright.sync_api import Page, expect


class MoviePage:
    """Проверки основных данных карточки без использования API."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.ui = load_config("settings.json")["ui"]

    @step("Открыть карточку по ID: {movie_id}")
    def open_by_id(self, movie_id: int) -> None:
        self.page.goto(
            urljoin(self.ui["base_url"], f"/film/{movie_id}/"),
            wait_until="domcontentloaded",
        )
        self.expect_id(movie_id)

    def expect_id(self, movie_id: int) -> None:
        """Проверить идентификатор непосредственно в маршруте карточки."""
        expect(self.page).to_have_url(
            re.compile(rf"/film/{movie_id}/?(?:[?#].*)?$")
        )

    def expect_year(self, year: int) -> None:
        """Проверить год в ссылке метаданных, а не в произвольном тексте."""
        year_link = (
            self.page.locator(f'a[href*="year--{year}"]')
            .filter(has_text=re.compile(rf"^\s*{year}\s*$"))
            .first
        )
        expect(year_link).to_be_visible()

    @step("Проверить название, год, постер и описание: {title}, {year}")
    def expect_main_details(self, title: str, year: int) -> None:
        expect(self.page.get_by_role("heading", level=1)).to_contain_text(
            title
        )
        self.expect_year(year)
        poster = self.page.locator(self.ui["selectors"]["poster"]).first
        expect(poster).to_be_visible()
        image = (
            poster
            if poster.evaluate("el => el.tagName === 'IMG'")
            else poster.locator("img").first
        )
        expect(image).to_be_visible()
        expect(image).to_have_js_property("complete", True)
        assert image.evaluate("el => el.naturalWidth > 0"), (
            "Постер не загружен"
        )
        description = self.page.locator(
            self.ui["selectors"]["description"]
        ).first
        expect(description).to_be_visible()
        expect(description).to_contain_text(re.compile(r"\S"))
