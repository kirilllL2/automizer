"""
Модуль действий для макросов.

Предоставляет функции для:
- Кликов (в точку, в область со случайным смещением)
- Распознавания областей на экране по пресетам
- Работы с координатами и областями
"""

import random
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

from src.config import get_config


# ============================================================================
# Типы данных
# ============================================================================

class Region:
    """Класс для представления области на экране."""
    
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        """
        Инициализирует область.
        
        Args:
            x1: Левая граница области.
            y1: Верхняя граница области.
            x2: Правая граница области.
            y2: Нижняя граница области.
        """
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
    
    @property
    def width(self) -> int:
        """Возвращает ширину области."""
        return self.x2 - self.x1
    
    @property
    def height(self) -> int:
        """Возвращает высоту области."""
        return self.y2 - self.y1
    
    @property
    def center(self) -> Tuple[int, int]:
        """Возвращает координаты центра области."""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)
    
    @property
    def area(self) -> int:
        """Возвращает площадь области."""
        return self.width * self.height
    
    def contains_point(self, x: int, y: int) -> bool:
        """Проверяет, находится ли точка внутри области."""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Возвращает кортеж (x1, y1, x2, y2)."""
        return (self.x1, self.y1, self.x2, self.y2)
    
    def __repr__(self) -> str:
        return f"Region(x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2})"


# ============================================================================
# Функции кликов
# ============================================================================

def click(x: int, y: int):
    """
    Выполняет клик в указанную точку.
    
    Args:
        x: Координата X.
        y: Координата Y.
    """
    try:
        from PyQt6.QtGui import QCursor
        from PyQt6.QtCore import QPoint
        from PyQt6.QtWidgets import QApplication
        
        # Получаем или создаем приложение
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        cursor = QCursor()
        cursor.setPos(QPoint(x, y))
        
        # Симуляция клика левой кнопкой мыши
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QMouseEvent
        
        # Отправляем события нажатия и отпускания кнопки
        QApplication.sendEvent(
            app.focusWidget() if app.focusWidget() else app.activeWindow(),
            QMouseEvent(
                QMouseEvent.Type.MouseButtonPress,
                cursor.pos(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier
            )
        )
        QApplication.sendEvent(
            app.focusWidget() if app.focusWidget() else app.activeWindow(),
            QMouseEvent(
                QMouseEvent.Type.MouseButtonRelease,
                cursor.pos(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier
            )
        )
        
        print(f"[Action] Клик в точке ({x}, {y})")
    except ImportError:
        print(f"[Action] Клик в точке ({x}, {y}) (симуляция)")


def click_in_region(
    region: Region,
    percent: Optional[float] = None,
    distribution: str = "uniform"
):
    """
    Выполняет клик в случайное место внутри области.
    
    Args:
        region: Область для клика.
        percent: Процент от центра области (0.0 - 1.0). 
                 Если None, берется из конфигурации (macros.default_click_percent).
                 0.0 = вся область, 1.0 = только центр.
        distribution: Тип распределения ("uniform" или "gaussian").
    
    Raises:
        ValueError: Если percent вне диапазона [0.0, 1.0].
    """
    # Получаем процент из конфига если не указан
    if percent is None:
        percent = get_config().get("macros", "default_click_percent", default=0.3)
    
    if not 0.0 <= percent <= 1.0:
        raise ValueError(f"percent должен быть в диапазоне [0.0, 1.0], получено {percent}")
    
    cx, cy = region.center
    half_width = region.width // 2
    half_height = region.height // 2
    
    # Вычисляем размер области для клика на основе процента
    effective_half_width = int(half_width * (1.0 - percent))
    effective_half_height = int(half_height * (1.0 - percent))
    
    if distribution == "uniform":
        # Равномерное распределение
        x = random.randint(cx - effective_half_width, cx + effective_half_width)
        y = random.randint(cy - effective_half_height, cy + effective_half_height)
    elif distribution == "gaussian":
        # Гауссово распределение (больше кликов ближе к центру)
        x = int(random.gauss(cx, effective_half_width / 3))
        y = int(random.gauss(cy, effective_half_height / 3))
        # Ограничиваем пределами области
        x = max(region.x1, min(region.x2, x))
        y = max(region.y1, min(region.y2, y))
    else:
        raise ValueError(f"Неизвестный тип распределения: {distribution}")
    
    click(x, y)


# ============================================================================
# Функции распознавания областей
# ============================================================================

def find_region(
    preset_id: str,
    confidence: Optional[float] = None,
    search_region: Optional[Region] = None
) -> Optional[Region]:
    """
    Находит область на экране по пресету скриншота.
    
    Args:
        preset_id: ID пресета скриншота для поиска.
        confidence: Порог уверенности (0.0 - 1.0). 
                   Если не указан, берется из конфигурации.
        search_region: Область для поиска (опционально). 
                      Если указана, поиск выполняется только в этой области.
    
    Returns:
        Region с координатами найденной области или None, если не найдено.
    
    Raises:
        FileNotFoundError: Если пресет не найден.
        RuntimeError: Если ошибка при загрузке CV модуля.
    """
    from src.cv import CVMatcher, MatchResult
    from src.screenshot import ScreenshotPresetStorage
    
    # Получаем путь к пресету
    preset_storage = ScreenshotPresetStorage()
    preset_info = preset_storage.get_preset(preset_id)
    
    if not preset_info:
        raise FileNotFoundError(f"Пресет с ID '{preset_id}' не найден")
    
    preset_path = preset_info.screenshot_path
    
    # Получаем уверенность из конфига если не указана
    if confidence is None:
        confidence = get_config().get("cv", "confidence_threshold", default=0.8)
    
    # Создаем matcher
    matcher = CVMatcher()
    
    try:
        if search_region is None:
            # Поиск по всему экрану
            result = matcher.find_match(
                preset_image_path=str(preset_path),
                preset_id=preset_id,
                preset_name=preset_info.name,
                confidence_threshold=confidence
            )
        else:
            # Поиск в указанной области
            result = _find_match_in_region(
                matcher=matcher,
                preset_image_path=str(preset_path),
                preset_id=preset_id,
                preset_name=preset_info.name,
                confidence_threshold=confidence,
                search_region=search_region
            )
        
        if result:
            region = Region(
                x1=result.x,
                y1=result.y,
                x2=result.x + result.width,
                y2=result.y + result.height
            )
            print(f"[CV] Найдена область: {region} (уверенность: {result.confidence:.2%})")
            return region
        else:
            print(f"[CV] Область для пресета '{preset_id}' не найдена")
            return None
            
    except Exception as e:
        print(f"[CV] Ошибка поиска области: {e}")
        return None


def _find_match_in_region(
    matcher: Any,
    preset_image_path: str,
    preset_id: str,
    preset_name: str,
    confidence_threshold: float,
    search_region: Region
) -> Optional[Any]:
    """
    Внутренняя функция для поиска совпадения в указанной области.
    
    Args:
        matcher: Экземпляр CVMatcher.
        preset_image_path: Путь к изображению пресета.
        preset_id: ID пресета.
        preset_name: Имя пресета.
        confidence_threshold: Порог уверенности.
        search_region: Область для поиска.
    
    Returns:
        MatchResult или None.
    """
    import cv2
    import numpy as np
    from PIL import ImageGrab
    
    # Загружаем изображение пресета
    template = cv2.imread(preset_image_path, cv2.IMREAD_COLOR)
    if template is None:
        raise ValueError(f"Не удалось загрузить изображение: {preset_image_path}")
    
    template_height, template_width = template.shape[:2]
    
    # Делаем скриншот только указанной области
    screenshot = ImageGrab.grab(bbox=search_region.to_tuple())
    screenshot_np = np.array(screenshot)
    
    # Конвертируем в формат OpenCV (RGB -> BGR)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Выполняем шаблонный поиск
    result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    
    # Находим лучшее совпадение
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Проверяем уверенность
    if max_val >= confidence_threshold:
        # Возвращаем координаты относительно всего экрана
        from src.cv import MatchResult
        return MatchResult(
            x=int(max_loc[0]) + search_region.x1,
            y=int(max_loc[1]) + search_region.y1,
            width=template_width,
            height=template_height,
            confidence=float(max_val),
            preset_id=preset_id,
            preset_name=preset_name,
        )
    
    return None


def find_all_regions(
    preset_id: str,
    confidence: Optional[float] = None,
    max_results: int = 10
) -> list[Region]:
    """
    Находит все области на экране по пресету скриншота.
    
    Args:
        preset_id: ID пресета скриншота для поиска.
        confidence: Порог уверенности (0.0 - 1.0).
        max_results: Максимальное количество результатов.
    
    Returns:
        Список Region с координатами всех найденных областей.
    """
    from src.cv import CVMatcher
    from src.screenshot import ScreenshotPresetStorage
    
    # Получаем путь к пресету
    preset_storage = ScreenshotPresetStorage()
    preset_info = preset_storage.get_preset(preset_id)
    
    if not preset_info:
        raise FileNotFoundError(f"Пресет с ID '{preset_id}' не найден")
    
    preset_path = preset_info.screenshot_path
    
    # Получаем уверенность из конфига если не указана
    if confidence is None:
        confidence = get_config().get("cv", "confidence_threshold", default=0.8)
    
    # Создаем matcher
    matcher = CVMatcher()
    
    results = matcher.find_all_matches(
        preset_image_path=str(preset_path),
        preset_id=preset_id,
        preset_name=preset_info.name,
        confidence_threshold=confidence,
        max_results=max_results
    )
    
    regions = []
    for result in results:
        region = Region(
            x1=result.x,
            y1=result.y,
            x2=result.x + result.width,
            y2=result.y + result.height
        )
        regions.append(region)
    
    print(f"[CV] Найдено {len(regions)} областей для пресета '{preset_id}'")
    return regions


def wait_for_region(
    preset_id: str,
    timeout: float = 10.0,
    interval: float = 0.5,
    confidence: Optional[float] = None,
    search_region: Optional[Region] = None
) -> Optional[Region]:
    """
    Ждет появления области на экране до истечения таймаута.
    
    Args:
        preset_id: ID пресета скриншота для поиска.
        timeout: Максимальное время ожидания в секундах.
        interval: Интервал между попытками в секундах.
        confidence: Порог уверенности.
        search_region: Область для поиска.
    
    Returns:
        Region с координатами найденной области или None, если таймаут истек.
    """
    import time
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        region = find_region(
            preset_id=preset_id,
            confidence=confidence,
            search_region=search_region
        )
        
        if region:
            return region
        
        time.sleep(interval)
    
    print(f"[CV] Таймаут ожидания области для пресета '{preset_id}'")
    return None


# ============================================================================
# Утилиты
# ============================================================================

def get_screen_size() -> Tuple[int, int]:
    """
    Возвращает размер экрана.
    
    Returns:
        Кортеж (width, height).
    """
    try:
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        screen = app.primaryScreen().geometry()
        return (screen.width(), screen.height())
    except ImportError:
        # Заглушка для тестирования
        return (1920, 1080)


def create_region_from_center(
    center_x: int,
    center_y: int,
    width: int,
    height: int
) -> Region:
    """
    Создает область с заданным центром и размерами.
    
    Args:
        center_x: Координата X центра.
        center_y: Координата Y центра.
        width: Ширина области.
        height: Высота области.
    
    Returns:
        Region с указанным центром и размерами.
    """
    x1 = center_x - width // 2
    y1 = center_y - height // 2
    x2 = center_x + width // 2
    y2 = center_y + height // 2
    
    return Region(x1, y1, x2, y2)


# Экспортируем основные функции для удобного импорта
__all__ = [
    'Region',
    'click',
    'click_in_region',
    'find_region',
    'find_all_regions',
    'wait_for_region',
    'get_screen_size',
    'create_region_from_center',
    'focus_window',
]


# ============================================================================
# Функции управления окнами
# ============================================================================

def focus_window(process_preset_id: str) -> bool:
    """
    Фокусируется на окне, связанном с пресетом процесса.
    
    Args:
        process_preset_id: ID пресета процесса (из presets.json).
    
    Returns:
        True, если фокус установлен успешно, False в противном случае.
    """
    from src.storage import PresetStorage
    from src.window_manager import WindowManager
    
    # Получаем хранилище пресетов нормализации
    preset_storage = PresetStorage()
    preset_info = preset_storage.get_preset(process_preset_id)
    
    if not preset_info:
        print(f"[Window] Пресет процесса '{process_preset_id}' не найден")
        return False
    
    # Ищем окно по имени процесса из пресета
    from src.normalizer import ProcessNormalizer
    normalizer = ProcessNormalizer()
    window = normalizer.find_window_by_process(preset_info.process_name)
    
    if not window:
        print(f"[Window] Окно для процесса '{preset_info.process_name}' не найдено")
        return False
    
    try:
        wm = WindowManager()
        success = wm.focus_window(window.window_id)
        if success:
            print(f"[Window] Фокус установлен на окне '{window.title}' (ID: {window.window_id})")
        else:
            print(f"[Window] Не удалось установить фокус на окне '{window.title}'")
        return success
    except Exception as e:
        print(f"[Window] Ошибка при фокусировке на окне: {e}")
        return False
