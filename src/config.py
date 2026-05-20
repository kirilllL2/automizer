"""
Модуль конфигурации приложения.

Управляет загрузкой и доступом к настройкам приложения из различных источников:
- default.yaml - значения по умолчанию
- config.yaml - пользовательские настройки
- переменные окружения (AUTOMIZER_*)
"""

import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    """Класс для управления конфигурацией приложения."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._config_dir: Path = Path.home() / ".automizer" / "config"
        self._default_config_path: Path = Path(__file__).parent.parent / "config" / "default.yaml"

    def load(self) -> None:
        """Загружает конфигурацию из всех источников."""
        # Загружаем значения по умолчанию
        self._config = self._load_yaml_file(self._default_config_path)

        # Загружаем пользовательские настройки (если существуют)
        user_config_path = self._config_dir / "config.yaml"
        if user_config_path.exists():
            user_config = self._load_yaml_file(user_config_path)
            self._config = self._deep_merge(self._config, user_config)

        # Переопределяем через переменные окружения
        self._load_from_env()

    def _load_yaml_file(self, path: Path) -> dict[str, Any]:
        """Загружает YAML файл."""
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load_from_env(self) -> None:
        """Загружает настройки из переменных окружения."""
        # Пример: AUTOMIZER_APP_DEBUG=true -> config['app']['debug'] = True
        for key, value in os.environ.items():
            if key.startswith("AUTOMIZER_"):
                parts = key[len("AUTOMIZER_") :].lower().split("_")
                self._set_nested_value(self._config, parts, self._parse_env_value(value))

    def _parse_env_value(self, value: str) -> Any:
        """Парсит значение переменной окружения в нужный тип."""
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    def _set_nested_value(
        self, d: dict[str, Any], keys: list[str], value: Any
    ) -> None:
        """Устанавливает значение вложенного ключа."""
        for key in keys[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        d[keys[-1]] = value

    def _deep_merge(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """Глубокое слияние словарей."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, *keys: str, default: Any = None) -> Any:
        """Получает значение по цепочке ключей."""
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @property
    def config_dir(self) -> Path:
        """Возвращает путь к директории конфигурации."""
        return self._config_dir


# Глобальный экземпляр конфигурации
config = Config()


def get_config() -> Config:
    """Возвращает глобальный экземпляр конфигурации."""
    return config
