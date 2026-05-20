"""
Модуль для нормализации окон процессов.

Предоставляет функциональность для:
- Нормализации положения и размера окон
- Применения пресетов к окнам
"""

from dataclasses import dataclass
from typing import Optional

from src.window_manager import WindowManager, WindowInfo


@dataclass
class NormalizationPreset:
    """Пресет для нормализации окна."""

    id: str
    name: str
    process_name: str  # Имя процесса или часть заголовка для поиска
    x: int
    y: int
    width: int
    height: int
    description: str = ""

    def __repr__(self) -> str:
        return f"NormalizationPreset(id={self.id}, name='{self.name}', process='{self.process_name}')"


class ProcessNormalizer:
    """Класс для нормализации положения и размера окон."""

    def __init__(self, window_manager: Optional[WindowManager] = None):
        self.window_manager = window_manager or WindowManager()

    def normalize_window(
        self,
        window_id: int,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> bool:
        """
        Нормализует окно - устанавливает его положение и размер.

        Args:
            window_id: Handle окна.
            x: Координата X (левый верхний угол).
            y: Координата Y (левый верхний угол).
            width: Ширина окна.
            height: Высота окна.

        Returns:
            True, если операция успешна.
        """
        return self.window_manager.set_window_position_and_size(
            window_id=window_id,
            x=x,
            y=y,
            width=width,
            height=height,
        )

    def apply_preset(self, preset: NormalizationPreset) -> bool:
        """
        Применяет пресет к найденному окну.

        Args:
            preset: Пресет для применения.

        Returns:
            True, если пресет успешно применен.
        """
        window = self.find_window_by_process(preset.process_name)
        if window is None:
            return False

        return self.normalize_window(
            window_id=window.window_id,
            x=preset.x,
            y=preset.y,
            width=preset.width,
            height=preset.height,
        )

    def find_window_by_process(self, process_identifier: str) -> Optional[WindowInfo]:
        """
        Ищет окно по идентификатору процесса (часть заголовка или имя процесса).

        Args:
            process_identifier: Строка для поиска в заголовке окна.

        Returns:
            WindowInfo или None, если окно не найдено.
        """
        windows = self.window_manager.get_windows()
        search_term = process_identifier.lower()

        for window in windows:
            if search_term in window.title.lower():
                return window

        return None

    def search_windows(self, query: str) -> list[WindowInfo]:
        """
        Ищет окна по поисковому запросу.

        Args:
            query: Поисковый запрос.

        Returns:
            Список найденных окон.
        """
        windows = self.window_manager.get_windows()
        if not query:
            return windows

        search_term = query.lower()
        return [
            window for window in windows
            if search_term in window.title.lower()
        ]
