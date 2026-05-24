"""
Модуль для работы со скриншотами.

Предоставляет функциональность для:
- Создания скриншотов выбранной области экрана
- Сохранения скриншотов в хранилище
- Удаления скриншотов
- Предварительного просмотра области выделения (полупрозрачная красная рамка)
- Разделения функций подсветки области и создания скриншота
- Пресетов скриншотов для быстрого захвата

Основные методы:
- `preview_area(x, y, width, height)` - показывает полупрозрачную красную рамку на экране
- `capture(x, y, width, height, ...)` - делает скриншот без превью
- `capture_with_preview(x, y, width, height, ...)` - сначала показывает превью, затем делает скриншот
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import get_config

from .presets import ScreenshotPreset, ScreenshotPresetStorage

__all__ = [
    "ScreenshotInfo",
    "ScreenshotManager",
    "ScreenshotPreset",
    "ScreenshotPresetStorage",
]


@dataclass
class ScreenshotInfo:
    """Информация о скриншоте."""

    id: str
    path: Path
    x: int
    y: int
    width: int
    height: int
    created_at: datetime
    description: str = ""


class ScreenshotManager:
    """Менеджер для управления скриншотами."""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Инициализирует менеджер скриншотов.

        Args:
            storage_path: Путь к директории для хранения скриншотов.
                         Если не указан, используется путь из конфигурации.
        """
        if storage_path is None:
            # Используем относительный путь в репозитории
            storage_path = Path(__file__).parent.parent.parent / "presets" / "screenshots"

        self.storage_path = storage_path
        self._screenshots: dict[str, ScreenshotInfo] = {}
        self._preview_duration: float = get_config().get(
            "screenshot", "preview_duration", default=1.0
        )
        self._load()

    def _load(self) -> None:
        """Загружает информацию о существующих скриншотах."""
        self._screenshots = {}
        if not self.storage_path.exists():
            return

        for file_path in self.storage_path.glob("*.png"):
            # Извлекаем ID из имени файла (формат: <id>.png)
            screenshot_id = file_path.stem
            # Пока не загружаем метаданные из отдельного файла
            # Можно расширить для хранения description и т.д.
            self._screenshots[screenshot_id] = ScreenshotInfo(
                id=screenshot_id,
                path=file_path,
                x=0,  # Неизвестно без метаданных
                y=0,
                width=0,
                height=0,
                created_at=datetime.fromtimestamp(file_path.stat().st_mtime),
            )

    def capture(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        screenshot_id: Optional[str] = None,
        description: str = "",
        output_path: Optional[str] = None,
    ) -> ScreenshotInfo:
        """
        Делает скриншот указанной области экрана.

        Args:
            x: Координата X верхнего левого угла.
            y: Координата Y верхнего левого угла.
            width: Ширина области.
            height: Высота области.
            screenshot_id: Уникальный идентификатор скриншота.
                          Если не указан, генерируется автоматически.
            description: Описание скриншота.
            output_path: Путь к файлу для сохранения (включая имя файла).
                        Если не указан, используется путь по умолчанию в хранилище.
                        Если файл существует, он будет перезаписан.

        Returns:
            Информация о созданном скриншоте.
        """
        if screenshot_id is None:
            screenshot_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        # Создаем директорию если не существует
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Определяем путь сохранения
        if output_path:
            # Если указан полный путь, используем его
            file_path = Path(output_path)
            # Убедимся, что директория существует
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Используем путь по умолчанию в хранилище
            file_path = self.storage_path / f"{screenshot_id}.png"

        # Делаем скриншот
        self._capture_area(x, y, width, height, file_path)

        screenshot_info = ScreenshotInfo(
            id=screenshot_id,
            path=file_path,
            x=x,
            y=y,
            width=width,
            height=height,
            created_at=datetime.now(),
            description=description,
        )
        self._screenshots[screenshot_id] = screenshot_info
        return screenshot_info

    def _capture_area(self, x: int, y: int, width: int, height: int, output_path: Path) -> None:
        """
        Захватывает область экрана и сохраняет в файл.

        Args:
            x: Координата X верхнего левого угла.
            y: Координата Y верхнего левого угла.
            width: Ширина области.
            height: Высота области.
            output_path: Путь для сохранения файла.
        """
        try:
            from PIL import ImageGrab
            bbox = (x, y, x + width, y + height)
            image = ImageGrab.grab(bbox=bbox)
            image.save(output_path, "PNG")
        except ImportError:
            # Fallback для систем без Pillow
            # В реальном приложении можно использовать другие библиотеки
            raise RuntimeError(
                "Для создания скриншотов требуется библиотека Pillow. "
                "Установите: pip install Pillow"
            )

    def preview_area(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """
        Показывает предварительный просмотр области выделения (красная рамка).

        Киллер-фича: на короткое время отображает красный прямоугольник
        вокруг области, которая будет захвачена.

        Args:
            x: Координата X верхнего левого угла.
            y: Координата Y верхнего левого угла.
            width: Ширина области.
            height: Высота области.
        """
        try:
            from PyQt6.QtWidgets import QApplication, QWidget
            from PyQt6.QtCore import Qt, QTimer
            from PyQt6.QtGui import QPainter, QPen, QBrush, QColor

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
            overlay.rect_params = (x, y, width, height)
            
            # Переопределяем метод paintEvent
            original_paint_event = overlay.paintEvent
            
            def paint_event(event):
                painter = QPainter(overlay)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                # Рисуем полупрозрачный фон
                painter.fillRect(overlay.rect(), QColor(0, 0, 0, 50))
                
                # Рисуем красную рамку
                pen = QPen(QColor(255, 0, 0), 3)
                painter.setPen(pen)
                brush = QBrush(QColor(255, 0, 0, 80))
                painter.setBrush(brush)
                
                x, y, w, h = overlay.rect_params
                painter.drawRect(x, y, w, h)
            
            overlay.paintEvent = paint_event
            overlay.show()
            
            # Ждем указанное время и закрываем
            QTimer.singleShot(int(self._preview_duration * 1000), overlay.close)
            
            # Запускаем цикл событий если нужно
            if app == QApplication.instance():
                app.processEvents()

        except Exception as e:
            # Если не удалось показать превью, просто продолжаем
            print(f"Не удалось показать превью: {e}")

    def capture_with_preview(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        screenshot_id: Optional[str] = None,
        description: str = "",
    ) -> ScreenshotInfo:
        """
        Делает скриншот с предварительным показом области выделения.

        Args:
            x: Координата X верхнего левого угла.
            y: Координата Y верхнего левого угла.
            width: Ширина области.
            height: Высота области.
            screenshot_id: Уникальный идентификатор скриншота.
            description: Описание скриншота.

        Returns:
            Информация о созданном скриншоте.
        """
        # Сначала показываем превью
        self.preview_area(x, y, width, height)

        # Затем делаем скриншот
        return self.capture(x, y, width, height, screenshot_id, description)

    def get_screenshot(self, screenshot_id: str) -> Optional[ScreenshotInfo]:
        """
        Получает информацию о скриншоте по ID.

        Args:
            screenshot_id: Идентификатор скриншота.

        Returns:
            Информация о скриншоте или None, если не найден.
        """
        return self._screenshots.get(screenshot_id)

    def get_all_screenshots(self) -> list[ScreenshotInfo]:
        """
        Получает все скриншоты.

        Returns:
            Список всех скриншотов.
        """
        return list(self._screenshots.values())

    def remove_screenshot(self, screenshot_id: str) -> bool:
        """
        Удаляет скриншот.

        Args:
            screenshot_id: Идентификатор скриншота для удаления.

        Returns:
            True, если скриншот удален, False если не найден.
        """
        if screenshot_id not in self._screenshots:
            return False

        screenshot = self._screenshots[screenshot_id]

        # Удаляем файл
        if screenshot.path.exists():
            screenshot.path.unlink()

        # Удаляем из словаря
        del self._screenshots[screenshot_id]
        return True

    def search_screenshots(self, query: str) -> list[ScreenshotInfo]:
        """
        Ищет скриншоты по запросу.

        Args:
            query: Поисковый запрос (ищет в ID и description).

        Returns:
            Список найденных скриншотов.
        """
        if not query:
            return self.get_all_screenshots()

        search_term = query.lower()
        return [
            screenshot for screenshot in self._screenshots.values()
            if (search_term in screenshot.id.lower() or
                search_term in screenshot.description.lower())
        ]
