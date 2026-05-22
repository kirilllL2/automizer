#!/usr/bin/env python3
"""
Automizer - Система нормализации окон процессов и управления скриншотами.
Главный файл запуска приложения.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь импорта
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """Точка входа в приложение."""
    app = QApplication(sys.argv)
    
    # Настраиваем стиль приложения
    app.setStyle("Fusion")
    
    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
