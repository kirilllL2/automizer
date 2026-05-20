"""
Модуль для работы со скриншотами.

Предоставляет функциональность для:
- Создания скриншотов выбранной области экрана
- Сохранения скриншотов в хранилище
- Удаления скриншотов
- Предварительного просмотра области выделения (полупрозрачная красная рамка)
- Разделения функций подсветки области и создания скриншота

Основные методы:
- `preview_area(x, y, width, height)` - показывает полупрозрачную красную рамку на экране
- `capture(x, y, width, height, ...)` - делает скриншот без превью
- `capture_with_preview(x, y, width, height, ...)` - сначала показывает превью, затем делает скриншот
"""

import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import get_config


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
            config = get_config()
            data_dir = Path(config.get("paths", "data_dir", default="~/.automizer/data")).expanduser()
            storage_path = data_dir / "screenshots"

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

        Returns:
            Информация о созданном скриншоте.

        Raises:
            ValueError: Если скриншот с таким ID уже существует.
        """
        if screenshot_id is None:
            screenshot_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        if screenshot_id in self._screenshots:
            raise ValueError(f"Скриншот с ID '{screenshot_id}' уже существует")

        # Создаем директорию если не существует
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Делаем скриншот
        file_path = self.storage_path / f"{screenshot_id}.png"
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
        Показывает предварительный просмотр области выделения (красный квадрат).

        Киллер-фича: на короткое время отображает красный прямоугольник
        вокруг области, которая будет захвачена.

        Args:
            x: Координата X верхнего левого угла.
            y: Координата Y верхнего левого угла.
            width: Ширина области.
            height: Высота области.
        """
        try:
            import tkinter as tk

            # Создаем полноэкранное прозрачное окно
            root = tk.Tk()
            root.attributes("-fullscreen", True)
            root.attributes("-topmost", True)
            root.overrideredirect(True)
            root.configure(bg="black")
            root.wm_attributes("-alpha", 0.2)  # Полностью прозрачный фон

            # Создаем Canvas на весь экран
            canvas = tk.Canvas(root, bg="black", highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)

            # Рисуем красный прямоугольник (рамку) вокруг целевой области
            # Используем create_rectangle с outline (красная рамка) и fill (полупрозрачный красный)
            canvas.create_rectangle(
                x, y, x + width, y + height,
                outline="red",
                width=3,
                fill="white"  # Узор для полупрозрачности
            )

            # Обновляем окно
            root.update()

            # Ждем указанное время
            time.sleep(self._preview_duration)

            # Закрываем окно
            root.destroy()

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
