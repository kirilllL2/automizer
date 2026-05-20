# Agents.md - Руководство для AI-агентов

Этот файл содержит информацию о проекте для помощи AI-агентам в разработке.

## О проекте

**Automizer** - большое десктопное Python приложение для автоматизации задач.

### Технологический стек

- **Python**: >= 3.10
- **Менеджер пакетов**: `uv` (современный, быстрый аналог pip/pipenv)
- **Конфигурация**: YAML файлы + переменные окружения
- **Тестирование**: pytest
- **Linting**: ruff, black, mypy

## Структура проекта

```
/workspace/
├── src/                  # Исходный код приложения
│   ├── __init__.py       # Инициализация пакета
│   ├── config.py         # Модуль конфигурации
│   └── ...               # Другие модули
├── config/               # Файлы конфигурации
│   └── default.yaml      # Настройки по умолчанию
├── tests/                # Тесты
│   ├── __init__.py
│   └── test_*.py
├── pyproject.toml        # Зависимости и настройки проекта
├── README.md             # Документация
└── Agents.md             # Этот файл
```

## Управление зависимостями

Все зависимости управляются через `pyproject.toml`:

- **Основные зависимости**: секция `[project.dependencies]`
- **Dev-зависимости**: секция `[project.optional-dependencies.dev]`

### Команды uv

```bash
# Синхронизировать зависимости
uv sync

# Синхронизировать с dev-зависимостями
uv sync --dev

# Добавить новую зависимость
uv add <package-name>

# Добавить dev-зависимость
uv add --dev <package-name>

# Запустить команду в виртуальном окружении
uv run <command>

# Установить пакет в режиме разработки
uv pip install -e .
```

## Конфигурация приложения

### Иерархия конфигурации (по возрастанию приоритета)

1. `config/default.yaml` - значения по умолчанию (в репозитории)
2. `~/.automizer/config/config.yaml` - пользовательские настройки
3. Переменные окружения с префиксом `AUTOMIZER_`

### Пример использования конфигурации

```python
from src.config import get_config

config = get_config()
config.load()

# Получить значение
debug_mode = config.get("app", "debug", default=False)
log_level = config.get("app", "log_level", default="INFO")
theme = config.get("ui", "theme", default="system")
```

### Преобразование переменных окружения

```
AUTOMIZER_APP_DEBUG=true      -> config['app']['debug'] = True
AUTOMIZER_UI_THEME=dark       -> config['ui']['theme'] = 'dark'
AUTOMIZER_UI_WINDOW_WIDTH=1400 -> config['ui']['window']['width'] = 1400
```

## Стандарты кода

### Форматирование

- **Line length**: 100 символов
- **Indentation**: 4 пробела
- **Formatter**: black
- **Linter**: ruff

### Типизация

- Использовать type hints для всех функций
- Строгий режим mypy

### Стиль кода

- Следовать PEP 8
- Использовать docstrings для публичных API
- Именовать переменные в snake_case
- Классы в PascalCase

## Тестирование

```bash
# Запустить все тесты
uv run pytest

# Запустить с покрытием
uv run pytest --cov=src

# Запустить конкретный тест
uv run pytest tests/test_specific.py -v
```

### Расположение тестов

Тесты находятся в директории `tests/`. naming convention: `test_<module>.py`

## Правила для AI-агентов

1. **Всегда проверяй существующий код** перед внесением изменений
2. **Следуй структуре проекта** - новые модули создавай в `src/`
3. **Пиши тесты** для нового функционала
4. **Используй типизацию** - добавляй type hints
5. **Проверяй код** перед коммитом:
   ```bash
   uv run ruff check src/
   uv run black --check src/
   uv run mypy src/
   ```
6. **Документируй** публичные API и сложные решения
7. **Не хардкодь** значения - выноси в конфигурацию
8. **Следи за зависимостями** - добавляй в `pyproject.toml` при необходимости

## Часто используемые паттерны

### Создание нового модуля

1. Создать файл в `src/<module_name>.py`
2. Добавить типизацию и docstring
3. Написать тесты в `tests/test_<module_name>.py`
4. Добавить зависимости в `pyproject.toml` если нужно
5. Проверить код линтерами

### Работа с конфигурацией

```python
from src.config import get_config

def initialize_app():
    config = get_config()
    config.load()
    
    debug = config.get("app", "debug", default=False)
    if debug:
        print("Debug mode enabled")
```

## Контакты и ресурсы

- Документация Python: https://docs.python.org/3/
- Документация uv: https://docs.astral.sh/uv/
- PEP 8: https://peps.python.org/pep-0008/
