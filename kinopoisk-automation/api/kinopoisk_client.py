"""Requests-клиент: отдельная сессия для каждого теста."""

import os
from dataclasses import dataclass, field
from typing import Any

import allure
import requests
from config.loader import load_config
from requests import Response


@dataclass(frozen=True)
class ApiSettings:
    """Токен исключён из repr и не прикладывается к Allure."""

    base_url: str
    timeout_seconds: float
    token: str = field(repr=False)

    @classmethod
    def from_environment(cls) -> "ApiSettings":
        """Прочитать публичные настройки и секрет из окружения."""
        settings = load_config("settings.json")["api"]
        return cls(
            base_url=os.getenv(
                "KINOPOISK_API_BASE_URL", settings["base_url"]
            ).rstrip("/"),
            timeout_seconds=float(
                os.getenv(
                    "KINOPOISK_API_TIMEOUT", str(settings["timeout_seconds"])
                )
            ),
            token=os.getenv("KINOPOISK_API_TOKEN", ""),
        )


class KinopoiskApiClient:
    """Общие заголовки, таймауты и безопасные диагностические вложения."""

    def __init__(self, settings: ApiSettings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> Response:
        """Выполнить GET, передавая фильтры через params и не логируя токен."""
        key = self.settings.token if token is None else token
        with allure.step(f"GET {path}"):
            response = self.session.get(
                f"{self.settings.base_url}/{path.lstrip('/')}",
                params=params,
                headers={"X-API-KEY": key},
                timeout=self.settings.timeout_seconds,
                allow_redirects=False,
            )
            # Ответ может теоретически отразить секрет: редактируем его.
            body = (
                response.text.replace(key, "[REDACTED]")
                if key
                else response.text
            )
            allure.attach(
                f"HTTP {response.status_code}\n{body[:20000]}",
                name="Ответ API (без заголовков запроса)",
                attachment_type=allure.attachment_type.TEXT,
            )
            return response

    def close(self) -> None:
        """Освободить сессию."""
        self.session.close()
