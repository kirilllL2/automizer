# Модуль нормализации процессов

Этот модуль предоставляет функциональность для нормализации (позиционирования и изменения размера) окон приложений, а также управления пресетами.

## Структура модулей

```
src/
├── window_manager.py      # Базовый API для работы с окнами Windows
├── normalizer/
│   └── __init__.py        # Логика нормализации окон и пресеты
├── storage/
│   └── __init__.py        # Хранилище пресетов (JSON)
├── ui/
│   ├── __init__.py
│   └── app.py             # Tkinter GUI приложение
└── cli.py                 # Консольный интерфейс с поддержкой пресетов
```

## Основные компоненты

### 1. ProcessNormalizer (`src/normalizer/__init__.py`)

Класс для нормализации положения и размера окон:

```python
from src.normalizer import ProcessNormalizer, NormalizationPreset

normalizer = ProcessNormalizer()

# Нормализовать окно (установить позицию и размер)
normalizer.normalize_window(window_id=12345, x=0, y=0, width=960, height=1080)

# Найти окно по части заголовка
window = normalizer.find_window_by_process("Chrome")

# Поиск окон по запросу
windows = normalizer.search_windows("browser")

# Применить пресет
preset = NormalizationPreset(
    id="browser_left",
    name="Browser Left",
    process_name="Chrome",
    x=0, y=0, width=960, height=1080
)
normalizer.apply_preset(preset)
```

### 2. PresetStorage (`src/storage/__init__.py`)

Хранилище пресетов с сохранением в JSON файл:

```python
from src.storage import PresetStorage

storage = PresetStorage()

# Добавить пресет
storage.add_preset(
    preset_id="browser_left",
    name="Browser Left",
    process_name="Chrome",
    x=0, y=0, width=960, height=1080,
    description="Браузер на левой половине экрана"
)

# Получить все пресеты
presets = storage.get_all_presets()

# Поиск пресетов
results = storage.search_presets("browser")

# Обновить пресет
storage.update_preset("browser_left", x=100, y=100)

# Удалить пресет
storage.remove_preset("browser_left")
```

### 3. GUI Приложение (`src/ui/app.py`)

Графический интерфейс на Tkinter для управления нормализацией:

**Запуск:**
```bash
python -m src.ui.app
```

**Возможности:**
- Выбор процесса из списка с поиском
- Установка положения и размера окна
- Быстрые пресеты расположения (половина экрана, четверти)
- Управление пресетами (добавление, редактирование, удаление, применение)

### 4. CLI (`src/cli.py`)

Консольный интерфейс с расширенной функциональностью:

**Запуск:**
```bash
python -m src.cli
```

**Новые команды:**

| Команда | Описание |
|---------|----------|
| `normalize <id> <x> <y> <w> <h>` | Нормализовать окно (позиция + размер) |
| `search <query>` | Поиск окон по заголовку |
| `presets`, `p` | Показать все пресеты |
| `preset_search <q>` | Поиск пресетов |
| `preset_apply <id>` | Применить пресет к окну |
| `preset_add <id> <name> <process> <x> <y> <w> <h> [desc]` | Добавить пресет |
| `preset_remove <id>` | Удалить пресет |
| `preset_edit <id> [--name=N] [--process=P] [--x=X] [--y=Y] [--w=W] [--h=H]` | Редактировать пресет |

**Примеры использования CLI:**

```bash
# Нормализовать окно на левую половину экрана
normalize 12345 0 0 960 1080

# Найти все окна Chrome
search chrome

# Добавить пресет
preset_add browser_left "Browser Left" Chrome 0 0 960 1080 "Браузер слева"

# Применить пресет
preset_apply browser_left

# Редактировать пресет
preset_edit browser_left --x=100 --y=100

# Удалить пресет
preset_remove browser_left
```

## Пресеты по умолчанию

В файле `config/default.yaml` определены пресеты по умолчанию:

```yaml
normalization:
  default_presets:
    - name: "Половина экрана слева"
      x: 0
      y: 0
      width: 960
      height: 1080
    - name: "Половина экрана справа"
      x: 960
      y: 0
      width: 960
      height: 1080
    - name: "Четверть экрана (верхний левый)"
      x: 0
      y: 0
      width: 960
      height: 540
```

## Хранение данных

Пресеты сохраняются в файле `~/.automizer/config/presets.json` в формате JSON:

```json
{
  "browser_left": {
    "id": "browser_left",
    "name": "Browser Left",
    "process_name": "Chrome",
    "x": 0,
    "y": 0,
    "width": 960,
    "height": 1080,
    "description": "Браузер на левой половине экрана"
  }
}
```

## Тесты

Все компоненты покрыты тестами:

```bash
pytest tests/test_normalizer.py -v
pytest tests/test_storage.py -v
```

## Зависимости

- **Windows**: pywin32 (для работы с окнами)
- **Linux/Mac**: stub-реализация для тестирования
- **GUI**: tkinter (встроен в Python)
- **CLI**: только стандартная библиотека

## Пример рабочего процесса

1. **Откройте приложения**, которые хотите расположить
2. **Запустите GUI**: `python -m src.ui.app`
3. **Выберите окно** из списка (можно использовать поиск)
4. **Укажите положение и размер** вручную или используйте быстрые пресеты
5. **Нажмите "Нормализовать окно"** для применения
6. **Сохраните как пресет** для быстрого применения в будущем
7. **В следующий раз** просто выберите пресет и примените его двойным кликом
