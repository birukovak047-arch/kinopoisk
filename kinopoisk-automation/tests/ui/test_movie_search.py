"""Пять независимых позитивных UI-сценариев из XLS."""

import allure
import pytest
from config.loader import load_config
from pages.movie_page import MoviePage
from pages.search_page import SearchPage
from playwright.sync_api import Page

DATA = load_config("test_data.json")
pytestmark = [pytest.mark.ui, allure.feature("Поиск и карточка фильма")]


@allure.id("214")
@allure.title("Поиск фильма по точному названию")
def test_search_movie_by_exact_title(page: Page) -> None:
    """FT-03 / TestIT 214: точное название и год в одной строке выдачи."""
    search = SearchPage(page)
    search.open()
    search.search(DATA["movie_title"])
    search.expect_movie_result(DATA["movie_title"], DATA["movie_year"])


@allure.id("215")
@allure.title("Поиск фильмов с фильтрами типа и года")
def test_search_movie_with_type_and_year_filters(page: Page) -> None:
    """FT-04 / TestIT 215: проверка до пяти результатов и их карточек."""
    search = SearchPage(page)
    search.open()
    search.apply_movie_year_filter(DATA["filter_year"], DATA["filter_type"])
    urls = search.filtered_movie_urls(
        DATA["filter_year"], DATA["filter_sample_size"]
    )
    # Нельзя ожидать Интерстеллар (2014) в выдаче за 2020 год.
    for url in urls:
        page.goto(url, wait_until="domcontentloaded")
        MoviePage(page).expect_year(DATA["filter_year"])


@allure.id("216")
@allure.title("Повторный поиск после изменения запроса")
def test_repeat_search_after_query_change(page: Page) -> None:
    """FT-05 / TestIT 216: первая и вторая выдача проверяются отдельно."""
    search = SearchPage(page)
    search.open()
    search.search(DATA["movie_title"])
    search.expect_movie_result(DATA["movie_title"], DATA["movie_year"])
    search.search(DATA["second_movie_title"])
    search.expect_movie_result(
        DATA["second_movie_title"], DATA["second_movie_year"]
    )


@allure.id("217")
@allure.title("Открытие карточки фильма из поиска")
def test_open_movie_card_from_search_results(page: Page) -> None:
    """FT-06 / TestIT 217: самостоятельно подготовить выдачу и открыть фильм."""
    search = SearchPage(page)
    search.open()
    search.search(DATA["movie_title"])
    search.open_movie_result(DATA["movie_title"], DATA["movie_year"])
    card = MoviePage(page)
    card.expect_id(DATA["movie_id"])
    card.expect_main_details(DATA["movie_title"], DATA["movie_year"])


@allure.id("218")
@allure.title("Открытие той же карточки по прямой ссылке в новой вкладке")
def test_open_movie_card_by_direct_link(page: Page) -> None:
    """FT-07 / TestIT 218: ссылка получается внутри этого же теста."""
    card = MoviePage(page)
    card.open_by_id(DATA["movie_id"])
    card.expect_main_details(DATA["movie_title"], DATA["movie_year"])
    copied_url = page.url
    new_tab = page.context.new_page()
    try:
        new_tab.goto(copied_url, wait_until="domcontentloaded")
        copied_card = MoviePage(new_tab)
        copied_card.expect_id(DATA["movie_id"])
        copied_card.expect_main_details(
            DATA["movie_title"], DATA["movie_year"]
        )
    finally:
        new_tab.close()
