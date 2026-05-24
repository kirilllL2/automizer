"""
Модуль пользовательского интерфейса Automizer.
Современный красивый резиновый интерфейс на PyQt6.
"""

# Избегаем импорта через __init__.py чтобы не загружать window_manager
from ui.main_window import MainWindow

__all__ = ["MainWindow", "MacrosWidget"]
