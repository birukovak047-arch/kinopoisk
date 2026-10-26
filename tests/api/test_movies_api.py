"""Три позитивных и два негативных API-теста из Google Docs."""

from typing import Any

import allure
import pytest
from api.kinopoisk_client import ApiSettings, KinopoiskApiClient
from config.loader import load_config
from requests import Response

DATA = load_config("test_data.json")
pytestmark = [pytest.mark.api, allure.feature("API каталога фильмов")]


def assert_json_response(response: Response) -> dict[str, Any]:
    """Не принимать HTML/капчу за JSON API."""
    assert (
        "application/json" in response.headers.get("Content-Type", "").lower()
    )
    payload = response.json()
    assert isinstance(payload, dict), "Ожидался объект JSON"
    return payload


def list_params() -> dict[str, Any]:
    """Новый словарь для каждого запроса — без общей изменяемой переменной."""
    return {"limit": DATA["page_limit"], "withCount": "false"}


@allure.id("API-1")
@allure.title("API ТС-1: список фильмов с действительным токеном")
def test_get_movies_with_valid_token(api_client: KinopoiskApiClient) -> None:
    """Проверить код, JSON, число записей и числовые ID."""
    response = api_client.get("/movie", params=list_params())
    assert response.status_code == 200
    docs = assert_json_response(response).get("docs")
    assert isinstance(docs, list)
    assert len(docs) == DATA["page_limit"]
    for movie in docs:
        assert isinstance(movie, dict)
        assert isinstance(movie.get("id"), int)


@allure.id("API-2")
@allure.title("API ТС-2: фильтры по названию и типу")
def test_get_movies_by_combined_filters(
    api_client: KinopoiskApiClient,
) -> None:
    """Проверить каждый результат, исключив пустую выдачу."""
    params = list_params()
    params.update({"type": "movie", "name": DATA["movie_title"]})
    response = api_client.get("/movie", params=params)
    assert response.status_code == 200
    docs = assert_json_response(response).get("docs")
    assert isinstance(docs, list) and docs
    assert len(docs) <= DATA["page_limit"]
    for movie in docs:
        assert movie.get("type") == "movie"
        assert movie.get("name") == DATA["movie_title"]


@allure.id("API-3")
@allure.title("API ТС-3: карточка по известному ID")
def test_get_movie_card_by_id(api_client: KinopoiskApiClient) -> None:
    """ID — независимые тестовые данные, а не результат другого теста."""
    response = api_client.get(f"/movie/{DATA['movie_id']}")
    assert response.status_code == 200
    payload = assert_json_response(response)
    assert payload.get("id") == DATA["movie_id"]
    assert payload.get("name") == DATA["movie_title"]


@allure.id("API-4")
@allure.title("API ТС-4: отказ при невалидном токене")
def test_get_movies_with_invalid_token(api_settings: ApiSettings) -> None:
    """Этот тест не требует наличия действительного токена."""
    client = KinopoiskApiClient(api_settings)
    try:
        invalid = load_config("settings.json")["api"]["invalid_token"]
        response = client.get("/movie", params=list_params(), token=invalid)
    finally:
        client.close()
    assert response.status_code == 401
    payload = assert_json_response(response)
    assert payload.get("statusCode") == 401
    assert payload.get("error") == "Unauthorized"
    assert payload.get("message") == DATA["unauthorized_message"]


@allure.id("API-5")
@allure.title("API ТС-5: ошибка для буквенного ID")
def test_get_movie_with_invalid_id(api_client: KinopoiskApiClient) -> None:
    """Проверить статус и обе ошибки валидации из исходного кейса."""
    response = api_client.get(f"/movie/{DATA['invalid_movie_id']}")
    assert response.status_code == 400
    payload = assert_json_response(response)
    assert payload.get("statusCode") == 400
    assert payload.get("error") == "Bad Request"
    messages = payload.get("message")
    assert isinstance(messages, list)
    assert set(messages) == set(DATA["invalid_id_messages"])
