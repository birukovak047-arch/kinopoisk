"""Page Object расширенного поиска и результатов."""

import re
from urllib.parse import urljoin

from allure import step
from config.loader import load_config
from playwright.sync_api import Locator, Page, expect


class SearchPage:
    """Локаторы вынесены в JSON и требуют сверки с доступным DOM."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.ui = load_config("settings.json")["ui"]
        self.selectors = self.ui["selectors"]

    @step("Открыть расширенный поиск")
    def open(self) -> None:
        self.page.goto(
            urljoin(self.ui["base_url"], self.ui["search_path"]),
            wait_until="domcontentloaded",
        )
        expect(
            self.page.locator(self.selectors["advanced_title"])
        ).to_be_visible()

    def title_input(self) -> Locator:
        """Найти видимое поле формы или шапки с явным ожиданием."""
        selector = (
            f"{self.selectors['advanced_title']}:visible, "
            f"{self.selectors['header_title']}:visible"
        )
        field = self.page.locator(selector).first
        expect(field).to_be_visible()
        return field

    def submit_form(self, field: Locator) -> None:
        """Отправить именно форму выбранного поля."""
        form = field.locator("xpath=ancestor::form[1]")
        button = form.locator(
            'input[type="submit"], button[type="submit"], button:not([type])'
        ).first
        expect(button).to_be_visible()
        button.click()
        expect(
            self.page.locator(self.selectors["results"]).first
        ).to_be_visible()

    @step("Найти фильм по названию: {title}")
    def search(self, title: str) -> None:
        field = self.title_input()
        field.fill(title)
        expect(field).to_have_value(title)
        # Расширенная форма отправляется кнопкой; шапка — Enter.
        if field.get_attribute("name") == "m_act[find]":
            self.submit_form(field)
        else:
            field.press("Enter")
        expect(
            self.page.locator(self.selectors["results"]).first
        ).to_be_visible()

    @step("Выбрать тип и год: {type_label}, {year}")
    def apply_movie_year_filter(self, year: int, type_label: str) -> None:
        type_select = self.page.locator(self.selectors["type"])
        year_select = self.page.locator(self.selectors["year"])
        expect(type_select).to_be_visible()
        expect(year_select).to_be_visible()
        type_select.select_option(label=type_label)
        year_select.select_option(label=str(year))
        expect(type_select.locator("option:checked")).to_have_text(type_label)
        expect(year_select.locator("option:checked")).to_have_text(str(year))
        self.submit_form(self.page.locator(self.selectors["advanced_title"]))

    def result(self, title: str, year: int) -> Locator:
        """Отличать фильм по точному названию и году внутри одной строки."""
        link = self.page.locator(self.selectors["result_title"]).filter(
            has_text=re.compile(rf"^\s*{re.escape(title)}\s*$")
        )
        row = self.page.locator(self.selectors["results"]).filter(has=link)
        row = row.filter(
            has=self.page.locator(self.selectors["result_year"]).filter(
                has_text=re.compile(rf"\b{year}\b")
            )
        ).first
        expect(row).to_be_visible()
        return row

    @step("Проверить результат: {title}, {year}")
    def expect_movie_result(self, title: str, year: int) -> None:
        row = self.result(title, year)
        expect(row.locator(self.selectors["result_title"])).to_have_attribute(
            "href", re.compile(r"/film/\d+")
        )

    @step("Открыть результат: {title}, {year}")
    def open_movie_result(self, title: str, year: int) -> None:
        self.result(title, year).locator(
            self.selectors["result_title"]
        ).click()
        expect(self.page).to_have_url(re.compile(r"/film/\d+"))

    @step("Проверить первые результаты фильтра: {year}")
    def filtered_movie_urls(self, year: int, sample_size: int) -> list[str]:
        """Проверить год каждой строки выборки и маршрут именно фильма."""
        rows = self.page.locator(self.selectors["results"])
        expect(rows.first).to_be_visible()
        count = min(rows.count(), sample_size)
        assert count > 0, "Фильтр вернул пустую выдачу"
        urls: list[str] = []
        for index in range(count):
            row = rows.nth(index)
            expect(row.locator(self.selectors["result_year"])).to_have_text(
                re.compile(rf"\b{year}\b")
            )
            link = row.locator(self.selectors["result_title"])
            expect(link).to_have_attribute("href", re.compile(r"/film/\d+"))
            href = link.get_attribute("href")
            assert href is not None
            urls.append(urljoin(self.ui["base_url"], href))
        return urls
