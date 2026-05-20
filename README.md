# Automizer

Большое десктопное Python приложение для автоматизации задач.

## Структура проекта

```
automizer/
├── src/              # Исходный код приложения
│   └── config.py     # Модуль конфигурации
├── config/           # Файлы конфигурации
│   └── default.yaml  # Настройки по умолчанию
├── tests/            # Тесты
├── pyproject.toml    # Зависимости и настройки проекта
└── README.md         # Этот файл
```

## Установка зависимостей

Проект использует `uv` для управления зависимостями:

```bash
# Установить uv (если не установлен)
pip install uv

# Установить все зависимости
uv sync

# Установить зависимости для разработки
uv sync --dev
```

## Конфигурация

Приложение поддерживает многоуровневую конфигурацию:

1. **Значения по умолчанию** - `config/default.yaml`
2. **Пользовательские настройки** - `~/.automizer/config/config.yaml`
3. **Переменные окружения** - префикс `AUTOMIZER_`

### Пример пользовательской конфигурации

Создайте файл `~/.automizer/config/config.yaml`:

```yaml
app:
  debug: true
  log_level: "DEBUG"

ui:
  theme: "dark"
  window:
    width: 1400
    height: 900
```

### Переменные окружения

```bash
export AUTOMIZER_APP_DEBUG=true
export AUTOMIZER_UI_THEME=dark
```

## Запуск

```bash
# В режиме разработки
uv run python -m src

# После установки
uv pip install -e .
```

## Разработка

```bash
# Запустить тесты
uv run pytest

# Проверка кода
uv run ruff check src/
uv run black --check src/
uv run mypy src/

# Форматирование кода
uv run black src/
uv run ruff check --fix src/
```

## Требования

- Python >= 3.10
- uv (менеджер пакетов)