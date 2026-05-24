# Модуль действий (Actions Module)

Модуль `src/macro/actions.py` предоставляет набор функций для автоматизации действий в макросах:
- Клики (в точку, в область со случайным смещением)
- Распознавание областей на экране по пресетам
- Работа с координатами и областями

## Установка

Для работы модуля требуются следующие библиотеки:
```bash
pip install PyQt6 opencv-python numpy Pillow
```

## Использование

### Импорт в макросах

```python
from src.macro import (
    Region,
    click,
    click_in_region,
    find_region,
    find_all_regions,
    wait_for_region,
    get_screen_size,
    create_region_from_center,
    delay,
)
```

Или напрямую из модуля actions:
```python
from src.macro.actions import Region, click, click_in_region, find_region
```

## Класс Region

Класс для представления области на экране.

### Создание области

```python
# По координатам углов
region = Region(x1=100, y1=100, x2=300, y2=200)

# Координаты автоматически нормализуются (x1 < x2, y1 < y2)
region = Region(300, 200, 100, 100)  # Будет преобразовано в (100, 100, 300, 200)
```

### Свойства

```python
region = Region(100, 100, 300, 200)

region.x1, region.y1  # Левый верхний угол: (100, 100)
region.x2, region.y2  # Правый нижний угол: (300, 200)
region.width          # Ширина: 200
region.height         # Высота: 100
region.center         # Центр: (200, 150)
region.area           # Площадь: 20000
```

### Методы

```python
# Проверка точки внутри области
region.contains_point(150, 150)  # True
region.contains_point(50, 50)    # False

# Преобразование в кортеж
region.to_tuple()  # (100, 100, 300, 200)
```

## Функции кликов

### click(x, y)

Выполняет клик в указанную точку.

```python
click(500, 300)  # Клик в точку (500, 300)
```

### click_in_region(region, percent=0.0, distribution="uniform")

Выполняет клик в случайное место внутри области.

**Параметры:**
- `region` - Область для клика
- `percent` - Процент от центра области (0.0 - 1.0):
  - `0.0` - вся область (по умолчанию)
  - `0.5` - 50% области от центра
  - `1.0` - только центр
- `distribution` - Тип распределения:
  - `"uniform"` - равномерное распределение (по умолчанию)
  - `"gaussian"` - гауссово распределение (больше кликов ближе к центру)

**Примеры:**

```python
region = Region(100, 100, 300, 200)

# Клик в случайное место во всей области
click_in_region(region, percent=0.0)

# Клик в случайное место в 50% области от центра
click_in_region(region, percent=0.5)

# Клик почти в центре (90% от центра)
click_in_region(region, percent=0.9)

# Клик с гауссовым распределением (чаще ближе к центру)
click_in_region(region, percent=0.5, distribution="gaussian")
```

## Распознавание областей

### find_region(preset_id, confidence=None, search_region=None)

Находит область на экране по пресету скриншота.

**Параметры:**
- `preset_id` - ID пресета скриншота для поиска
- `confidence` - Порог уверенности (0.0 - 1.0). Если не указан, берется из конфигурации
- `search_region` - Область для поиска (опционально). Если указана, поиск выполняется только в этой области

**Возвращает:**
- `Region` с координатами найденной области или `None`, если не найдено

**Примеры:**

```python
# Поиск по всему экрану с уверенностью из конфига
region = find_region("my_button")

# Поиск с переопределением порога уверенности
region = find_region("my_button", confidence=0.9)

# Поиск только в указанной области
search_area = Region(0, 0, 400, 300)
region = find_region("my_button", confidence=0.8, search_region=search_area)

if region:
    print(f"Найдена область: {region}")
    # Клик в центр найденной области
    cx, cy = region.center
    click(cx, cy)
else:
    print("Область не найдена")
```

### find_all_regions(preset_id, confidence=None, max_results=10)

Находит все области на экране по пресету скриншота.

**Параметры:**
- `preset_id` - ID пресета скриншота
- `confidence` - Порог уверенности (0.0 - 1.0)
- `max_results` - Максимальное количество результатов

**Возвращает:**
- Список `Region` всех найденных областей

**Пример:**

```python
regions = find_all_regions("my_button", confidence=0.8, max_results=5)
print(f"Найдено областей: {len(regions)}")

for i, region in enumerate(regions, 1):
    print(f"{i}. {region}")
```

### wait_for_region(preset_id, timeout=10.0, interval=0.5, confidence=None, search_region=None)

Ждет появления области на экране до истечения таймаута.

**Параметры:**
- `preset_id` - ID пресета скриншота
- `timeout` - Максимальное время ожидания в секундах
- `interval` - Интервал между попытками в секундах
- `confidence` - Порог уверенности
- `search_region` - Область для поиска

**Возвращает:**
- `Region` с координатами найденной области или `None`, если таймаут истек

**Пример:**

```python
print("Ожидание появления кнопки...")
region = wait_for_region(
    preset_id="start_button",
    timeout=30.0,      # Ждать до 30 секунд
    interval=0.5,      # Проверять каждые 0.5 секунды
    confidence=0.8
)

if region:
    print(f"Кнопка найдена: {region}")
    click_in_region(region, percent=0.3)
else:
    print("Таймаут ожидания истек")
```

## Утилиты

### get_screen_size()

Возвращает размер экрана.

```python
width, height = get_screen_size()
print(f"Размер экрана: {width}x{height}")
```

### create_region_from_center(center_x, center_y, width, height)

Создает область с заданным центром и размерами.

```python
# Создать область 200x150 с центром в точке (600, 400)
region = create_region_from_center(
    center_x=600,
    center_y=400,
    width=200,
    height=150
)
print(region)  # Region(x1=500, y1=325, x2=700, y2=475)
```

## Полный пример макроса

```python
"""Макрос: Автоматический клик по кнопке"""

from src.macro import (
    Region,
    click,
    click_in_region,
    find_region,
    wait_for_region,
    delay,
)

NAME = "Автоклик по кнопке"
DESCRIPTION = "Находит кнопку и кликает в неё"


def run():
    # Ждем появления кнопки (до 10 секунд)
    button_region = wait_for_region(
        preset_id="start_button",
        timeout=10.0,
        confidence=0.8
    )
    
    if not button_region:
        print("Кнопка не найдена, завершаем")
        return
    
    print(f"Кнопка найдена: {button_region}")
    
    # Кликаем в случайное место в центральной части кнопки (30% от центра)
    click_in_region(button_region, percent=0.3)
    
    # Небольшая задержка
    delay(0.5)
    
    # Клик в другую точку
    click(500, 300)
    
    print("Макрос завершен")
```

## Конфигурация

Порог уверенности по умолчанию берется из конфигурационного файла (`config/default.yaml`):

```yaml
cv:
  confidence_threshold: 0.8  # Порог уверенности по умолчанию
  search_timeout: 5.0        # Таймаут поиска
  preview_duration: 2.0      # Длительность показа превью
```

В функциях распознавания можно переопределить значение уверенности:

```python
# Использовать уверенность 0.9 вместо 0.8 из конфига
region = find_region("my_button", confidence=0.9)
```

## Пресеты скриншотов

Для использования функций распознавания необходимо создать пресеты скриншотов.
Пресеты хранятся в файле `presets/screenshot_presets.json`, а изображения - в `presets/screenshots/`.

Пример пресета:
```json
{
  "my_button": {
    "id": "my_button",
    "name": "Кнопка Старт",
    "screenshot_path": "presets/screenshots/my_button.png",
    "process_preset_id": "",
    "x": 100,
    "y": 100,
    "width": 80,
    "height": 30,
    "description": "Кнопка запуска"
  }
}
```
