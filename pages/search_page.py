import re
from urllib.parse import quote, urljoin
from allure import step
from config.loader import load_config
from playwright.sync_api import Locator, Page, expect


class SearchPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.ui = load_config("settings.json")["ui"]
        self.selectors = self.ui["selectors"]

    # ---------- Сценарии через главную страницу (/new-search/) ----------

    @step("Открыть главную страницу")
    def open(self) -> None:
        self.page.goto(
            urljoin(self.ui["base_url"], self.ui["search_path"]),
            wait_until="domcontentloaded",
        )
        expect(
            self.page.locator(self.selectors["header_search"]).first
        ).to_be_visible()

    def header_input(self) -> Locator:
        field = self.page.locator(self.selectors["header_search"]).first
        expect(field).to_be_visible()
        return field

    @step("Найти фильм по названию: {title}")
    def search(self, title: str) -> None:
        field = self.header_input()
        field.click()
        field.fill(title)
        expect(field).to_have_value(title)
        field.press("Enter")
        # После Enter уходим на /new-search/?text=..., ждём появления выдачи
        expect(
            self.page.locator(self.selectors["results_header"]).first
        ).to_be_visible(timeout=20000)

    @step("Проверить, что в выдаче есть фильм: {title} ({year})")
    def expect_movie_result(self, title: str, year: int) -> None:
        pattern = re.compile(rf"^\s*{re.escape(title)}\b.*\b{year}\b")
        link = self.page.locator(self.selectors["results_header"]).filter(
            has_text=pattern
        ).first
        expect(link).to_be_visible(timeout=20000)
        (expect(link).to_have_attribute
         ("href", re.compile(r"/(film|series)/\d+")))

    @step("Открыть карточку фильма: {title} ({year})")
    def open_movie_result(self, title: str, year: int) -> None:
        pattern = re.compile(rf"^\s*{re.escape(title)}\b.*\b{year}\b")
        link = self.page.locator(self.selectors["results_header"]).filter(
            has_text=pattern
        ).first
        expect(link).to_be_visible(timeout=20000)
        link.click()
        expect(self.page).to_have_url(re.compile(r"/(film|series)/\d+"))

    # ---------- Сценарии через расширенный поиск (/s/) ----------

    @step("Открыть /s/ с фильтрами: {type_label}, {year}, {title}")
    def apply_movie_year_filter(
            self, year: int, type_label: str, title: str
    ) -> None:
        self.page.goto(
            f"{self.ui['base_url']}/s/",
            wait_until="domcontentloaded"
        )
        form = self.page.locator('#formSearchMain')
        (form.locator
         ('input[name="m_act[find]"]').fill(title))
        (form.locator
         ('select[name="m_act[from_year]"]').select_option(str(year)))
        (form.locator
         ('select[name="m_act[to_year]"]').select_option(str(year)))
        (form.locator
         ('select[name="m_act[content_find]"]').select_option('film'))
        form.locator('input[value="поиск"]').click()
        expect(
            self.page.locator(self.selectors["results_advanced"]).first
        ).to_be_visible(timeout=20000)

    @step("Проверить первые результаты фильтра: {year}")
    def filtered_movie_urls(self, year: int, sample_size: int) -> list[str]:
        """Проверить год каждой строки выборки и маршрут именно фильма."""
        rows = self.page.locator(self.selectors["results_advanced"])
        expect(rows.first).to_be_visible(timeout=20000)
        count = min(rows.count(), sample_size)
        assert count > 0, "Фильтр вернул пустую выдачу"
        urls: list[str] = []
        for index in range(count):
            row = rows.nth(index)
            expect(row.locator(self.selectors
                               ["result_year_advanced"])).to_have_text(
                re.compile(rf"\b{year}\b")
            )
            link = row.locator(self.selectors["result_title_advanced"])
            expect(link).to_have_attribute("href", re.compile(r"/film/\d+"))
            href = link.get_attribute("href")
            assert href is not None
            urls.append(urljoin(self.ui["base_url"], href))
        return urls
