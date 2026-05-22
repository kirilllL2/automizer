"""
Модуль компьютерного зрения (CV) для поиска областей на скриншотах.

Предоставляет функциональность для:
- Поиска области на экране, совпадающей с предоставленным изображением (preset)
- Настройки уверенности (confidence threshold) через конфигурацию
- Подсветки найденной области
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple
import time

from src.config import get_config


@dataclass
class MatchResult:
    """Результат поиска совпадения изображения."""
    
    x: int  # Координата X верхнего левого угла найденной области
    y: int  # Координата Y верхнего левого угла найденной области
    width: int  # Ширина найденной области
    height: int  # Высота найденной области
    confidence: float  # Уверенность совпадения (0.0 - 1.0)
    preset_id: str  # ID пресета, по которому искали
    preset_name: str  # Имя пресета


class CVMatcher:
    """Класс для поиска совпадений изображений на экране."""
    
    def __init__(self):
        """Инициализирует CV matcher."""
        self._confidence_threshold: float = get_config().get(
            "cv", "confidence_threshold", default=0.8
        )
        self._search_timeout: float = get_config().get(
            "cv", "search_timeout", default=5.0
        )
    
    def find_match(
        self,
        preset_image_path: str,
        preset_id: str,
        preset_name: str,
        confidence_threshold: Optional[float] = None,
    ) -> Optional[MatchResult]:
        """
        Ищет область на экране, совпадающую с предоставленным изображением.
        
        Args:
            preset_image_path: Путь к изображению пресета для поиска.
            preset_id: ID пресета.
            preset_name: Имя пресета.
            confidence_threshold: Порог уверенности (переопределяет значение из конфига).
        
        Returns:
            MatchResult с координатами найденной области или None, если совпадение не найдено.
        """
        threshold = confidence_threshold if confidence_threshold is not None else self._confidence_threshold
        
        try:
            import cv2
            import numpy as np
        except ImportError:
            raise RuntimeError(
                "Для работы CV модуля требуется OpenCV и NumPy. "
                "Установите: pip install opencv-python numpy"
            )
        
        # Загружаем изображение пресета
        preset_path = Path(preset_image_path)
        if not preset_path.exists():
            raise FileNotFoundError(f"Изображение пресета не найдено: {preset_image_path}")
        
        template = cv2.imread(str(preset_path), cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"Не удалось загрузить изображение: {preset_image_path}")
        
        template_height, template_width = template.shape[:2]
        
        # Делаем скриншот всего экрана
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)
        
        # Конвертируем в формат OpenCV (RGB -> BGR)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Выполняем шаблонный поиск
        result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        
        # Находим лучшее совпадение
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Проверяем уверенность
        if max_val >= threshold:
            return MatchResult(
                x=int(max_loc[0]),
                y=int(max_loc[1]),
                width=template_width,
                height=template_height,
                confidence=float(max_val),
                preset_id=preset_id,
                preset_name=preset_name,
            )
        
        return None
    
    def find_all_matches(
        self,
        preset_image_path: str,
        preset_id: str,
        preset_name: str,
        confidence_threshold: Optional[float] = None,
        max_results: int = 10,
    ) -> List[MatchResult]:
        """
        Ищет все области на экране, совпадающие с предоставленным изображением.
        
        Args:
            preset_image_path: Путь к изображению пресета для поиска.
            preset_id: ID пресета.
            preset_name: Имя пресета.
            confidence_threshold: Порог уверенности (переопределяет значение из конфига).
            max_results: Максимальное количество результатов.
        
        Returns:
            Список MatchResult с координатами всех найденных областей.
        """
        threshold = confidence_threshold if confidence_threshold is not None else self._confidence_threshold
        
        try:
            import cv2
            import numpy as np
        except ImportError:
            raise RuntimeError(
                "Для работы CV модуля требуется OpenCV и NumPy. "
                "Установите: pip install opencv-python numpy"
            )
        
        # Загружаем изображение пресета
        preset_path = Path(preset_image_path)
        if not preset_path.exists():
            raise FileNotFoundError(f"Изображение пресета не найдено: {preset_image_path}")
        
        template = cv2.imread(str(preset_path), cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"Не удалось загрузить изображение: {preset_image_path}")
        
        template_height, template_width = template.shape[:2]
        
        # Делаем скриншот всего экрана
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)
        
        # Конвертируем в формат OpenCV (RGB -> BGR)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Выполняем шаблонный поиск
        result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        
        # Находим все совпадения выше порога
        locations = np.where(result >= threshold)
        
        matches = []
        used_positions = set()
        
        for pt in zip(*locations[::-1]):
            # Проверяем, не слишком ли близко к уже найденным
            is_duplicate = False
            for existing_x, existing_y in used_positions:
                if abs(pt[0] - existing_x) < template_width // 2 and \
                   abs(pt[1] - existing_y) < template_height // 2:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                matches.append(MatchResult(
                    x=int(pt[0]),
                    y=int(pt[1]),
                    width=template_width,
                    height=template_height,
                    confidence=float(result[pt[1], pt[0]]),
                    preset_id=preset_id,
                    preset_name=preset_name,
                ))
                used_positions.add((pt[0], pt[1]))
                
                if len(matches) >= max_results:
                    break
        
        # Сортируем по уверенности
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        return matches
    
    def preview_match(
        self,
        result: MatchResult,
        duration: float = 2.0,
    ) -> None:
        """
        Показывает превью найденной области (белая рамка в черном квадрате).
        
        Args:
            result: Результат поиска для отображения.
            duration: Длительность показа в секундах.
        """
        try:
            from PyQt6.QtWidgets import QApplication, QWidget
            from PyQt6.QtCore import Qt, QTimer
            from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
            
            # Создаем приложение если его нет
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # Создаем полноэкранное прозрачное окно
            overlay = QWidget()
            overlay.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )
            overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            overlay.setGeometry(0, 0, app.primaryScreen().geometry().width(),
                               app.primaryScreen().geometry().height())
            
            # Сохраняем параметры для отрисовки
            overlay.match_result = result
            
            # Переопределяем метод paintEvent
            def paint_event(event):
                painter = QPainter(overlay)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                # Рисуем полупрозрачный черный фон
                painter.fillRect(overlay.rect(), QColor(0, 0, 0, 150))
                
                # Рисуем белую рамку вокруг найденной области
                x, y, w, h = result.x, result.y, result.width, result.height
                pen = QPen(QColor(255, 255, 255), 4)
                painter.setPen(pen)
                brush = QBrush(QColor(255, 255, 255, 50))
                painter.setBrush(brush)
                painter.drawRect(x, y, w, h)
                
                # Рисуем информацию о совпадении
                font = QFont("Segoe UI", 14, QFont.Weight.Bold)
                painter.setFont(font)
                painter.setPen(QColor(255, 255, 255))
                
                info_text = f"{result.preset_name}\nУверенность: {result.confidence:.1%}"
                painter.drawText(x, y - 10, info_text)
            
            overlay.paintEvent = paint_event
            overlay.show()
            
            # Ждем указанное время и закрываем
            QTimer.singleShot(int(duration * 1000), overlay.close)
            
            # Запускаем цикл событий если нужно
            if app == QApplication.instance():
                app.processEvents()
                
        except Exception as e:
            print(f"Не удалось показать превью CV: {e}")
