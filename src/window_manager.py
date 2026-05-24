"""
Модуль для управления окнами приложений на Windows.

Предоставляет функциональность для:
- Получения списка запущенных процессов (окон)
- Изменения положения окон на экране
- Фокусировки на окнах
- Изменения размера окон
- Получения скриншотов области окна (даже если оно не активно)
"""

from dataclasses import dataclass
from typing import Optional
import win32gui
import win32process
import win32con
import win32ui
WIN32_AVAILABLE = True


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
        if not WIN32_AVAILABLE:
            return "Test Window"
        try:
            title = win32gui.GetWindowText(hwnd)
            if title and title.strip():
                return title
            return None
        except Exception:
            return None

    def _get_window_pid(self, hwnd: int) -> Optional[int]:
        """Получает PID процесса, которому принадлежит окно."""
        if not WIN32_AVAILABLE:
            return 1234
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

    def capture_window_area(
        self,
        window_id: int,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: str,
    ) -> bool:
        """
        Делает скриншот области окна по относительным координатам.
        
        Важно: Эта функция работает даже если окно находится за другими окнами
        или не активно, так как использует DC (Device Context) окна напрямую.
        
        Args:
            window_id: Handle окна.
            x: Относительная координата X внутри окна (от левого верхнего угла окна).
            y: Относительная координата Y внутри окна (от левого верхнего угла окна).
            width: Ширина области для захвата.
            height: Высота области для захвата.
            output_path: Путь для сохранения файла скриншота.
            
        Returns:
            True, если операция успешна.
        """
        try:
            # Получаем DC окна
            hwnd_dc = win32gui.GetWindowDC(window_id)
            
            # Создаем совместимый DC
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            # Создаем битмап
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            
            # Выбираем битмап в DC
            save_dc.SelectObject(bitmap)
            
            # Копируем область из окна в битмап
            # BitBlt копирует указанную область из исходного DC в целевой
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (x, y), win32con.SRCCOPY)
            
            # Сохраняем битмап в файл
            bitmap.SaveBitmapFile(save_dc, output_path)
            
            # Освобождаем ресурсы
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(window_id, hwnd_dc)
            
            return True
        except Exception as e:
            print(f"Ошибка при захвате области окна: {e}")
            return False

    def click_in_window(
        self,
        window_id: int,
        x: int,
        y: int,
        percent: float = 0.5,
    ) -> bool:
        """
        Выполняет клик в указанной области окна используя низкоуровневое взаимодействие.
        
        Этот метод использует Windows API для эмуляции клика мыши, что позволяет
        работать с оконными приложениями (включая Unity игры), которые могут не
        реагировать на стандартные методы симуляции кликов.
        
        Args:
            window_id: Handle окна.
            x: Относительная координата X внутри области (0-1).
            y: Относительная координата Y внутри области (0-1).
            percent: Процент от размера области для клика (0.0-1.0). По умолчанию 0.5 (центр).
            
        Returns:
            True, если операция успешна.
        """
        try:
            import ctypes
            from ctypes import wintypes
            
            # Получаем координаты окна
            left, top, right, bottom = win32gui.GetWindowRect(window_id)
            window_width = right - left
            window_height = bottom - top
            
            # Вычисляем абсолютные координаты клика
            abs_x = left + int(window_width * x)
            abs_y = top + int(window_height * y)
            
            # Перемещаем курсор
            ctypes.windll.user32.SetCursorPos(abs_x, abs_y)
            
            # Небольшая задержка для стабильности
            import time
            time.sleep(0.05)
            
            # Эмулируем нажатие и отпускание левой кнопки мыши
            # MOUSEEVENTF_LEFTDOWN = 0x0002
            # MOUSEEVENTF_LEFTUP = 0x0004
            ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
            
            return True
        except Exception as e:
            print(f"Ошибка при клике в окно: {e}")
            return False
