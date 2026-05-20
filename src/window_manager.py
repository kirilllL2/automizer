"""
Модуль для управления окнами приложений на Windows.

Предоставляет функциональность для:
- Получения списка запущенных процессов (окон)
- Изменения положения окон на экране
- Фокусировки на окнах
- Изменения размера окон
"""

from dataclasses import dataclass
from typing import Optional

import win32gui
import win32process
import win32con


@dataclass
class WindowInfo:
    """Информация об окне."""

    window_id: int
    title: str
    pid: Optional[int]
    x: int
    y: int
    width: int
    height: int

    def __repr__(self) -> str:
        return f"WindowInfo(id={self.window_id}, title='{self.title}', pid={self.pid})"


class WindowManager:
    """Класс для управления окнами приложений на Windows."""

    def get_windows(self) -> list[WindowInfo]:
        """
        Получает список всех видимых окон.

        Returns:
            Список объектов WindowInfo с информацией об окнах.
        """
        windows = []
        
        def enum_callback(hwnd: int, results: list) -> bool:
            """Callback для EnumWindows."""
            # Проверяем, видно ли окно
            if win32gui.IsWindowVisible(hwnd):
                info = self._get_window_info(hwnd)
                if info:
                    results.append(info)
            return True
        
        results: list[WindowInfo] = []
        win32gui.EnumWindows(enum_callback, results)
        
        return results

    def _get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """
        Получает информацию об окне.

        Args:
            hwnd: Handle окна.

        Returns:
            WindowInfo или None, если окно не имеет заголовка.
        """
        try:
            # Получаем заголовок окна
            title = self._get_window_title(hwnd)
            if not title:
                return None

            # Получаем PID окна
            pid = self._get_window_pid(hwnd)

            # Получаем геометрию окна
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            
            return WindowInfo(
                window_id=hwnd,
                title=title,
                pid=pid,
                x=left,
                y=top,
                width=right - left,
                height=bottom - top,
            )
        except Exception:
            return None

    def _get_window_title(self, hwnd: int) -> Optional[str]:
        """Получает заголовок окна."""
        try:
            title = win32gui.GetWindowText(hwnd)
            if title and title.strip():
                return title
            return None
        except Exception:
            return None

    def _get_window_pid(self, hwnd: int) -> Optional[int]:
        """Получает PID процесса, которому принадлежит окно."""
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return pid
        except Exception:
            return None

    def move_window(
        self, window_id: int, x: int, y: int
    ) -> bool:
        """
        Перемещает окно в указанные координаты.

        Args:
            window_id: Handle окна.
            x: Новая координата X (левый верхний угол).
            y: Новая координата Y (левый верхний угол).

        Returns:
            True, если операция успешна.
        """
        try:
            # Получаем текущий размер окна
            left, top, right, bottom = win32gui.GetWindowRect(window_id)
            width = right - left
            height = bottom - top
            
            # Перемещаем окно
            win32gui.MoveWindow(window_id, x, y, width, height, True)
            return True
        except Exception:
            return False

    def resize_window(
        self, window_id: int, width: int, height: int
    ) -> bool:
        """
        Изменяет размер окна.

        Args:
            window_id: Handle окна.
            width: Новая ширина.
            height: Новая высота.

        Returns:
            True, если операция успешна.
        """
        try:
            # Получаем текущую позицию окна
            left, top, right, bottom = win32gui.GetWindowRect(window_id)
            
            # Изменяем размер окна
            win32gui.MoveWindow(window_id, left, top, width, height, True)
            return True
        except Exception:
            return False

    def focus_window(self, window_id: int) -> bool:
        """
        Фокусируется на окне.

        Args:
            window_id: Handle окна.

        Returns:
            True, если операция успешна.
        """
        try:
            # Восстанавливаем окно, если оно свернуто
            if win32gui.IsIconic(window_id):
                win32gui.ShowWindow(window_id, win32con.SW_RESTORE)
            
            # Выводим окно на передний план
            win32gui.SetForegroundWindow(window_id)
            return True
        except Exception:
            return False

    def set_window_position_and_size(
        self,
        window_id: int,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> bool:
        """
        Устанавливает положение и/или размер окна.

        Args:
            window_id: Handle окна.
            x: Новая координата X (None = не менять).
            y: Новая координата Y (None = не менять).
            width: Новая ширина (None = не менять).
            height: Новая высота (None = не менять).

        Returns:
            True, если операция успешна.
        """
        try:
            # Получаем текущие параметры
            left, top, right, bottom = win32gui.GetWindowRect(window_id)
            
            # Используем текущие значения, если новые не указаны
            new_x = x if x is not None else left
            new_y = y if y is not None else top
            new_width = width if width is not None else (right - left)
            new_height = height if height is not None else (bottom - top)
            
            # Устанавливаем новые параметры
            win32gui.MoveWindow(window_id, new_x, new_y, new_width, new_height, True)
            return True
        except Exception:
            return False
