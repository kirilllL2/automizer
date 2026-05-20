"""Tests for config module."""

import os
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.config import Config


@pytest.fixture
def config():
    """Создает экземпляр Config для тестов."""
    return Config()


def test_config_get_default_value(config):
    """Тест получения значения по умолчанию."""
    # Изначально конфигурация пуста
    value = config.get("nonexistent", "key", default="default_value")
    assert value == "default_value"


def test_config_deep_merge():
    """Тест глубокого слияния словарей."""
    config = Config()
    
    base = {"app": {"debug": False, "name": "test"}, "ui": {"theme": "light"}}
    override = {"app": {"debug": True}, "ui": {"language": "ru"}}
    
    result = config._deep_merge(base, override)
    
    assert result["app"]["debug"] is True
    assert result["app"]["name"] == "test"
    assert result["ui"]["theme"] == "light"
    assert result["ui"]["language"] == "ru"


def test_config_parse_env_value(config):
    """Тест парсинга значений переменных окружения."""
    assert config._parse_env_value("true") is True
    assert config._parse_env_value("True") is True
    assert config._parse_env_value("1") is True
    assert config._parse_env_value("false") is False
    assert config._parse_env_value("0") is False
    assert config._parse_env_value("42") == 42
    assert config._parse_env_value("3.14") == 3.14
    assert config._parse_env_value("string") == "string"


def test_config_set_nested_value(config):
    """Тест установки вложенного значения."""
    d = {"app": {}}
    config._set_nested_value(d, ["app", "debug"], True)
    assert d["app"]["debug"] is True
    
    config._set_nested_value(d, ["ui", "theme", "name"], "dark")
    assert d["ui"]["theme"]["name"] == "dark"


def test_config_load_from_env(config):
    """Тест загрузки из переменных окружения."""
    with patch.dict(os.environ, {"AUTOMIZER_APP_DEBUG": "true"}):
        config._config = {}
        config._load_from_env()
        assert config._config["app"]["debug"] is True
