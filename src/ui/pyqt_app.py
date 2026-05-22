"""
Простой PyQt интерфейс с кнопкой для создания скриншота.
"""

import sys
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen


class ScreenshotApp(QMainWindow):
    """Простое приложение с одной кнопкой для создания скриншота."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle("📸 Скриншоты")
        self.setMinimumSize(300, 200)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title_label = QLabel("Создание скриншотов")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2b2d42;")
        layout.addWidget(title_label)
        
        # Подзаголовок
        subtitle_label = QLabel("Нажмите кнопку ниже, чтобы сделать скриншот всего экрана")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 12px; color: #5e6472;")
        layout.addWidget(subtitle_label)
        
        # Кнопка для создания скриншота
        self.screenshot_button = QPushButton("📷 Сделать скриншот")
        self.screenshot_button.setMinimumHeight(50)
        self.screenshot_button.setStyleSheet("""
            QPushButton {
                background-color: #00adb5;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00d4dc;
            }
            QPushButton:pressed {
                background-color: #008b91;
            }
        """)
        self.screenshot_button.clicked.connect(self._take_screenshot)
        layout.addWidget(self.screenshot_button)
        
        # Метка статуса
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #4caf50; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Добавляем растягиватель, чтобы прижать контент к центру
        layout.addStretch()
        
        central_widget.setLayout(layout)

    def _take_screenshot(self) -> None:
        """Сделать скриншот всего экрана и сохранить его."""
        try:
            # Получаем скриншот
            screen = QScreen.grabWindow(QApplication.primaryScreen())
            
            if screen is None:
                QMessageBox.critical(self, "Ошибка", "Не удалось сделать скриншот")
                return
            
            # Создаем директорию для скриншотов
            screenshots_dir = Path(__file__).parent.parent.parent / "screenshots"
            screenshots_dir.mkdir(exist_ok=True)
            
            # Генерируем имя файла с датой и временем
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = screenshots_dir / filename
            
            # Сохраняем скриншот
            screen.save(str(filepath))
            
            # Обновляем статус
            self.status_label.setText(f"✓ Скриншот сохранен: {filename}")
            self.status_label.setStyleSheet("color: #4caf50; font-size: 12px; font-weight: bold;")
            
            print(f"Скриншот сохранен: {filepath}")
            
        except Exception as e:
            self.status_label.setText(f"✗ Ошибка: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336; font-size: 12px;")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сделать скриншот: {str(e)}")


def main():
    """Точка входа в приложение."""
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль приложения
    app.setStyleSheet("""
        QMainWindow {
            background-color: #edf2f4;
        }
    """)
    
    window = ScreenshotApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
