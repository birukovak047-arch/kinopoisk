# Автоматизация тестирования Кинопоиска

Python 3.11+, pytest, Requests, Playwright (Chromium), Allure.
Проект построен по общей идее примера Chitai-gorod: Page Objects,
отдельный API-клиент, настройки и два независимых набора тестов

## Покрытие и трассировка

| Источник | Сценарий | Автотест |
|---|---|---|
| XLS, TestIT 214 / FT-03 | Точное название и год | test_search_movie_by_exact_title |
| XLS, TestIT 215 / FT-04 | Тип фильм и год 2020 | test_search_movie_with_type_and_year_filters |
| XLS, TestIT 216 / FT-05 | Изменение поискового запроса | test_repeat_search_after_query_change |
| XLS, TestIT 217 / FT-06 | Карточка из выдачи | test_open_movie_card_from_search_results |
| XLS, TestIT 218 / FT-07 | Прямая ссылка в новой вкладке | test_open_movie_card_by_direct_link |
| Google Docs, ТС-1 | Список с действительным токеном | test_get_movies_with_valid_token |
| Google Docs, ТС-2 | Фильтры имени и типа | test_get_movies_by_combined_filters |
| Google Docs, ТС-3 | Карточка по ID | test_get_movie_card_by_id |
| Google Docs, ТС-4 | Невалидный токен | test_get_movies_with_invalid_token |
| Google Docs, ТС-5 | Буквенный ID | test_get_movie_with_invalid_id |

UI: пять позитивных сценариев. API: три позитивных, два негативных.
Авторизация Яндекса не включена: выбранные пять сценариев не требуют
личного аккаунта.


## Структура

```text
api/kinopoisk_client.py       Requests-клиент
config/settings.json         адреса, таймауты, UI-селекторы
config/test_data.json        названия, ID, годы, ожидаемые ошибки
config/loader.py             чтение конфигурации
pages/search_page.py         форма поиска и результаты
pages/movie_page.py          карточка фильма
tests/ui/test_movie_search.py пять UI-тестов
tests/api/test_movies_api.py  пять API-тестов
conftest.py                  фикстуры, запуск браузера, Allure-вложения
pytest.ini                   маркеры и настройки pytest
requirements.txt             только используемые Python-зависимости
```

## Установка

В каталоге распакованного проекта:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Затем:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

На Linux при недостающих системных библиотеках используйте
`python -m playwright install --with-deps chromium` с нужными правами.
Драйверы Selenium не нужны, бинарные файлы браузера в Git не добавляются.

## Получение токена
 1. Перейти по ссылке на официальный сайт кинопоиска для работы с API:
https://poiskkino.dev/?spm=a2ty_o01.29997173.0.0.6469c921XZKs0e
 2. Проскроллить страницу до конца и нажать "Получить токен в телеграмм"
 3. Подписаться на канал кинопоиска и получить токен в сообщении

Демо: 200 запросов в сутки. 
Токен работает, пока пользователь в чате @omdb_dev и на канале @mdwit0r.

Windows PowerShell:

```powershell
$env:KINOPOISK_API_TOKEN = "НОВЫЙ_ТОКЕН"
```

macOS/Linux:

```bash
export KINOPOISK_API_TOKEN="НОВЫЙ_ТОКЕН"
```

## Запуск из корня проекта

```bash
pytest --collect-only -q
pytest tests/ui --headed
pytest tests/api
pytest
```

Запуск одного сценария:

```bash
pytest tests/ui/test_movie_search.py::test_search_movie_by_exact_title --headed
pytest tests/api/test_movies_api.py::test_get_movie_card_by_id
```

Каждый UI-тест получает новый контекст и самостоятельно готовит данные.
Каждый API-тест получает собственную Requests-сессию, не использует ID
из чужого теста. Запросы только GET. Порядок запуска не имеет значения.
Нет time.sleep(), stealth, обхода CAPTCHA или отключения TLS-проверки.
При CAPTCHA/403/429 остановите прогон, сохраните свидетельства и согласуйте
другой сценарий или стенд. Не запускайте параллельно и не устраивайте
нагрузочный прогон на продакшене. Защита не считается успешным тестом.

## Allure

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

Allure CLI устанавливается отдельно от Python-зависимостей;
для Allure Report 2 требуется Java. Проверить установку: `allure --version`.
Без CLI pytest создаст файлы результатов, но HTML-отчет не откроется.
В отчет попадают шаги, ответы API без заголовков и скриншот при UI-ошибке.
Перед публикацией дополнительно проверьте вложения на персональные данные.
