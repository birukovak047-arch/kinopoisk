# Автоматизация тестирования Кинопоиска

Python 3.11+, pytest, Requests, Playwright (Chromium), Allure.
Проект построен по общей идее примера Chitai-gorod: Page Objects,
отдельный API-клиент, настройки и два независимых набора тестов.
Это не копия исходного репозитория и не подтверждение работы локаторов.

## Состояние проекта

Подготовлен код реальных интеграционных тестов, без mock-подмен.
Статическая проверка и сбор тестов выполнены; сетевые сценарии и браузер
на живом сайте не запускались. Поэтому утверждать, что тесты пройдены,
нельзя. UI-селекторы в config/settings.json — кандидаты для сверки с DOM
в вашем окружении. Текст страницы расширенного поиска был доступен,
но интерактивные действия и DOM-локаторы не проверены браузером.
Если верстка отличается, исправьте селекторы, не ослабляя проверки.

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
личного аккаунта. Нефункциональный чек-лист выполняется вручную.
Все выбранные функциональные и API-кейсы также проходят вручную:
автоматизация не заменяет ручной прогон.

## Уточнения исходных API-кейсов

Используется реальный адрес из переданного документа:
https://api.poiskkino.dev/v1.5. Это отдельный сервис, не веб-сайт
www.kinopoisk.ru. Посещать сайт перед API-запросом не требуется.
В ТС-5 в исходнике смешаны v1.4 и v1.5: выбран v1.5, как в основном URL.
Кавычки вокруг названия фильма в ТС-2 считаются оформлением текста,
а не частью имени: Requests кодирует параметр name=Интерстеллар.
Карточка ТС-3 проверяется как один JSON-объект, не список из одного элемента.
ID 258687 хранится в тестовых данных и не зависит от другого автотеста.
Коды 401/400 и сообщения ошибок взяты из пользовательского документа,
не подтверждены выполненными запросами. При расхождении с фактическим
контрактом сначала уточните документацию и ручной кейс; не принимайте
несколько случайных кодов только для получения зеленого результата.
ТС-6 с курсорной пагинацией не входит в выбранный набор.

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

## Секреты и настройки

В исходном Google Docs опубликован API-токен. Его значение в проект
не перенесено. Отзовите опубликованный токен и получите новый перед
использованием публичного репозитория. Не добавляйте секрет в JSON,
README, Allure-вложения или GitHub. При необходимости ограничьте доступ
к исходному документу. Если секрет попал в Git, удаления файла мало:
сначала отзовите секрет, затем очистите историю.

Windows PowerShell:

```powershell
$env:KINOPOISK_API_TOKEN = "НОВЫЙ_ТОКЕН"
```

macOS/Linux:

```bash
export KINOPOISK_API_TOKEN="НОВЫЙ_ТОКЕН"
```

Дополнительные переменные: KINOPOISK_API_BASE_URL и KINOPOISK_API_TIMEOUT.
Без токена четыре API-теста завершатся ошибкой настройки; это не skip
и не успешное прохождение. Тест с невалидным токеном работает отдельно.

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

## Первичная адаптация и сдача

1. Установите зависимости, проверьте сбор десяти тестов.
2. В видимом браузере проверьте селекторы расширенной формы, строк
   выдачи, постера и описания; уточните их в config/settings.json.
3. Выполните выбранные кейсы вручную, сопоставьте контракт API.
4. Запустите UI и API отдельно, затем все тесты и Allure.
5. Проверьте отсутствие секретов, кешей и браузерных бинарных файлов.
6. Создайте публичный репозиторий GitHub и загрузите исходники.

Публикация (после создания пустого репозитория в GitHub):

```bash
git init
git add .
git commit -m "Add Kinopoisk UI and API autotests"
git branch -M main
git remote add origin https://github.com/YOUR_LOGIN/kinopoisk-automation.git
git push -u origin main
```

Ссылки на исходники требований:
https://github.com/tuse4ka1984/Chitai-gorod
https://docs.google.com/document/d/1kiVvCZUTy3nJ5gsR6nG9w4QY388sWazCf0_E7pHDxRQ/edit
Функциональные сценарии взяты из приложенного экспорта XLS TestIT.
