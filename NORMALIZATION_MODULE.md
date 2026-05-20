# Модуль нормализации процессов

Этот модуль предоставляет функциональность для нормализации (позиционирования и изменения размера) окон приложений, а также управления пресетами.

## Структура проекта

```
workspace/
├── src/
│   ├── __init__.py
│   ├── window_manager.py       # Базовый API для работы с окнами (Windows/Linux stub)
│   ├── window_manager_stub.py  # Stub-реализация для Linux/Mac
│   ├── config.py               # Конфигурация приложения
│   ├── cli.py                  # Консольный интерфейс
│   ├── normalizer/
│   │   └── __init__.py         # ProcessNormalizer, NormalizationPreset
│   ├── storage/
│   │   └── __init__.py         # PresetStorage (JSON хранилище)
│   └── ui/
│       ├── __init__.py
│       └── app.py              # Tkinter GUI приложение
├── tests/
│   ├── test_normalizer.py      # Тесты нормализатора
│   ├── test_storage.py         # Тесты хранилища
│   └── test_config.py          # Тесты конфигурации
├── config/
│   └── default.yaml            # Пресеты по умолчанию
├── NORMALIZATION_MODULE.md     # Эта документация
└── README.md                   # Основная документация проекта
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

**Методы ProcessNormalizer:**

| Метод | Описание |
|-------|----------|
| `normalize_window(window_id, x, y, width, height)` | Установить позицию и размер окна |
| `find_window_by_process(process_name)` | Найти окно по имени процесса |
| `search_windows(query)` | Поиск окон по подстроке в заголовке |
| `apply_preset(preset)` | Применить пресет к окну |
| `get_screen_size()` | Получить размер экрана |

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

**Методы PresetStorage:**

| Метод | Описание |
|-------|----------|
| `add_preset(id, name, process_name, x, y, width, height, description)` | Добавить новый пресет |
| `remove_preset(preset_id)` | Удалить пресет по ID |
| `update_preset(preset_id, **kwargs)` | Обновить поля пресета |
| `get_preset(preset_id)` | Получить пресет по ID |
| `get_all_presets()` | Получить все пресеты |
| `search_presets(query)` | Поиск пресетов по name/process/description |

### 3. GUI Приложение (`src/ui/app.py`)

Графический интерфейс на Tkinter для управления нормализацией:

**Запуск:**
```bash
python -m src.ui.app
```

**Возможности:**
- **Две вкладки** для разделения workflows:
  1. **📋 Выбор процесса** — выбор окна из списка с поиском и установка позиции/размера
  2. **💾 Управление пресетами** — просмотр, применение, редактирование и удаление пресетов
- Поиск окон по заголовку с живым фильтром
- Быстрые пресеты расположения (половина экрана, четверти)
- Кнопка "Сохранить как пресет" автоматически подставляет текущие параметры окна в диалог создания
- Двойной клик по пресету для быстрого применения
- Современный темный дизайн с цветовой схемой и emoji-иконками

**Интерфейс:**

**Вкладка 1 "Выбор процесса":**
- Список всех открытых окон с поиском
- Панель установки координат (X, Y) и размеров (Ширина, Высота)
- Кнопки быстрых пресетов: ½ экрана ←/→, ¼ ↖↗↙↘
- Кнопки действий: "✅ Нормализовать окно", "💾 Сохранить как пресет"

**Вкладка 2 "Управление пресетами":**
- Список сохранённых пресетов с поиском
- Отображение: имя, процесс, позиция/размер
- Кнопки: "▶ Применить", "✏️ Редактировать", "🗑️ Удалить"

**Стилистика:**
- Темная цветовая схема (#2b2d42, #3d405b, #00adb5)
- Современные шрифты Segoe UI
- Emoji-иконки для лучшей навигации
- Увеличенные отступы для удобства
- Подсветка выбранных элементов

**Workflow сохранения пресета:**
1. Выберите окно на вкладке "Выбор процесса"
2. Настройте позицию и размер (вручную или через быстрые пресеты)
3. Нажмите "💾 Сохранить как пресет"
4. Откроется диалог с **уже заполненными полями**:
   - Имя (на основе заголовка окна)
   - Процесс (заголовок окна)
   - X, Y, Ширина, Высота (текущие значения)
   - Описание (пустое, для заполнения)
5. Отредактируйте при необходимости и нажмите "✅ Сохранить"
6. Автоматическое переключение на вкладку "Управление пресетами"

### 4. CLI (`src/cli.py`)

Консольный интерфейс с расширенной функциональностью:

**Запуск:**
```bash
python -m src.cli
```

**Команды CLI:**

| Команда | Описание |
|---------|----------|
| `list`, `l` | Показать все окна |
| `normalize <id> <x> <y> <w> <h>` | Нормализовать окно (позиция + размер) |
| `search <query>` | Поиск окон по заголовку |
| `presets`, `p` | Показать все пресеты |
| `preset_search <q>` | Поиск пресетов |
| `preset_apply <id>` | Применить пресет к окну |
| `preset_add <id> <name> <process> <x> <y> <w> <h> [desc]` | Добавить пресет |
| `preset_remove <id>` | Удалить пресет |
| `preset_edit <id> [--name=N] [--process=P] [--x=X] [--y=Y] [--w=W] [--h=H]` | Редактировать пресет |
| `help`, `h` | Показать справку |
| `exit`, `quit` | Выход из CLI |

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
# Запустить все тесты
pytest tests/ -v

# Тесты нормализатора
pytest tests/test_normalizer.py -v

# Тесты хранилища
pytest tests/test_storage.py -v

# Тесты конфигурации
pytest tests/test_config.py -v
```

**Статус тестов:** ✅ 35 тестов проходят успешно

## Зависимости

| Компонент | Зависимости |
|-----------|-------------|
| **Windows** | pywin32 (для работы с окнами) |
| **Linux/Mac** | stub-реализация для тестирования |
| **GUI** | tkinter (встроен в Python) |
| **CLI** | только стандартная библиотека |
| **Тесты** | pytest, pytest-cov |

**Установка зависимостей:**
```bash
pip install pywin32  # Только для Windows
pip install pytest pytest-cov  # Для тестов
```

## Пример рабочего процесса

### Через GUI (рекомендуется)

#### Сценарий 1: Нормализация окна

1. **Откройте приложения**, которые хотите расположить
2. **Запустите GUI**: `python -m src.ui.app`
3. **Перейдите на вкладку "📋 Выбор процесса"**
4. **Найдите нужное окно** в списке или используйте поиск (например, "Chrome")
5. **Кликните по окну** — текущие координаты и размер автоматически заполнятся в поля справа
6. **Настройте положение и размер**:
   - Вручную через поля X, Y, Ширина, Высота
   - Или используйте быстрые пресеты: "½ экрана ←", "½ экрана →", "¼ ↖↗↙↘"
7. **Нажмите "✅ Нормализовать окно"** — окно переместится и изменит размер

#### Сценарий 2: Создание пресета

1. На вкладке "📋 Выбор процесса" выберите окно и настройте его положение/размер
2. **Нажмите "💾 Сохранить как пресет"**
3. Откроется диалог с **автоматически заполненными полями**:
   - Имя:基于窗口标题
   - Процесс: заголовок окна
   - X, Y, Ширина, Высота: текущие значения
4. **Отредактируйте имя** (например, "Рабочее место Chrome")
5. **Добавьте описание** (опционально)
6. **Нажмите "✅ Сохранить"**
7. Приложение автоматически переключит на вкладку "💾 Управление пресетами"

#### Сценарий 3: Применение пресета

1. **Перейдите на вкладку "💾 Управление пресетами"**
2. **Найдите нужный пресет** (можно использовать поиск)
3. **Примените пресет** одним из способов:
   - Двойной клик по пресету
   - Выбрать пресет и нажать "▶ Применить"
4. Если окно с указанным процессом найдено — оно будет нормализовано

#### Сценарий 4: Редактирование пресета

1. На вкладке "💾 Управление пресетами" выберите пресет
2. Нажмите "✏️ Редактировать"
3. Измените параметры (имя, процесс, координаты, размеры)
4. Нажмите "✅ Сохранить"

### Через CLI

```bash
# 1. Найти ID окна
python -m src.cli search chrome

# 2. Нормализовать окно
python -m src.cli normalize 12345 0 0 960 1080

# 3. Создать пресет для будущего использования
python -m src.cli preset_add browser_left "Browser Left" Chrome 0 0 960 1080 "Браузер слева"

# 4. В следующий раз просто применить пресет
python -m src.cli preset_apply browser_left
```

## API для разработчиков

### Создание собственного пресета программно

```python
from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.storage import PresetStorage

# Инициализация
normalizer = ProcessNormalizer()
storage = PresetStorage()

# Создание пресета
preset = NormalizationPreset(
    id="my_preset",
    name="My Custom Layout",
    process_name="Chrome",
    x=100,
    y=100,
    width=800,
    height=600,
    description="Custom layout for Chrome"
)

# Сохранение пресета
storage.add_preset(
    preset_id=preset.id,
    name=preset.name,
    process_name=preset.process_name,
    x=preset.x,
    y=preset.y,
    width=preset.width,
    height=preset.height,
    description=preset.description
)

# Применение пресета
normalizer.apply_preset(preset)
```

### Поиск и фильтрация окон

```python
from src.normalizer import ProcessNormalizer

normalizer = ProcessNormalizer()

# Получить все окна
all_windows = normalizer.get_all_windows()

# Поиск по заголовку
chrome_windows = normalizer.search_windows("Chrome")

# Найти конкретное окно по имени процесса
window = normalizer.find_window_by_process("notepad")
```

## Структура данных пресета

```python
class NormalizationPreset:
    id: str              # Уникальный идентификатор
    name: str            # Отображаемое имя
    process_name: str    # Имя процесса для поиска
    x: int               # Позиция X (левый верхний угол)
    y: int               # Позиция Y (левый верхний угол)
    width: int           # Ширина окна
    height: int          # Высота окна
    description: str     # Описание (опционально)
```

## Возможные улучшения

- [ ] Поддержка нескольких мониторов
- [ ] Анимация перемещения окон
- [ ] Горячие клавиши для быстрого применения пресетов
- [ ] Экспорт/импорт пресетов в JSON/YAML
- [ ] Группировка пресетов по категориям
- [ ] Авто-применение пресетов при запуске приложений
