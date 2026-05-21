"""
UI модуль для управления нормализацией процессов и скриншотами.

Современный PyQt5 интерфейс с красивым дизайном:
- Градиентные фоны и элементы
- Тени и эффекты свечения
- Овальные кнопки с анимацией при наведении
- Адаптивная резиновая верстка
- Плавные переходы между состояниями
"""

import sys
from typing import Optional
from dataclasses import dataclass

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QListWidget, QListWidgetItem,
    QTabWidget, QMessageBox, QSizePolicy,
    QGraphicsDropShadowEffect, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QCursor

from src.window_manager import WindowManager, WindowInfo
from src.normalizer import ProcessNormalizer
from src.storage import PresetStorage
from src.screenshot import ScreenshotManager
from src.screenshot.presets import ScreenshotPresetStorage


@dataclass
class ColorPalette:
    primary_start = "#667eea"
    primary_end = "#764ba2"
    secondary_start = "#f093fb"
    secondary_end = "#f5576c"
    accent_success_start = "#4facfe"
    accent_success_end = "#00f2fe"
    bg_dark = "#1a1a2e"
    bg_card = "#16213e"
    bg_card_hover = "#1f2b47"
    text_primary = "#ffffff"
    text_secondary = "#a0a0a0"
    border_light = "rgba(255, 255, 255, 0.1)"
    border_accent = "rgba(102, 126, 234, 0.3)"


COLORS = ColorPalette()


class CardFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
        self._setup_shadow()
        
    def _setup_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS.bg_card};
                border-radius: 16px;
                border: 1px solid {COLORS.border_light};
            }}
            QFrame:hover {{
                background-color: {COLORS.bg_card_hover};
                border: 1px solid {COLORS.border_accent};
            }}
        """)
        
    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)


class OvalButton(QPushButton):
    def __init__(self, text="", parent=None, gradient_type="primary"):
        super().__init__(text, parent)
        self.gradient_type = gradient_type
        self._setup_style()
        self._setup_shadow()
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
    def _get_gradient(self):
        gradients = {
            "primary": (COLORS.primary_start, COLORS.primary_end),
            "secondary": (COLORS.secondary_start, COLORS.secondary_end),
            "success": (COLORS.accent_success_start, COLORS.accent_success_end),
        }
        return gradients.get(self.gradient_type, (COLORS.primary_start, COLORS.primary_end))
        
    def _setup_style(self):
        start, end = self._get_gradient()
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {start}, stop:1 {end});
                border: none;
                border-radius: 25px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 30px;
            }}
            QPushButton:hover {{
                padding: 14px 32px;
            }}
        """)
        
    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)


class SearchInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS.bg_dark};
                border: 2px solid {COLORS.border_light};
                border-radius: 25px;
                padding: 12px 20px;
                color: {COLORS.text_primary};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS.primary_start};
            }}
        """)


class ModernListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                padding: 10px;
            }}
            QListWidget::item {{
                background-color: {COLORS.bg_card};
                border-radius: 12px;
                padding: 15px;
                margin: 5px 0;
                border: 1px solid {COLORS.border_light};
            }}
            QListWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.primary_start}, stop:1 {COLORS.primary_end});
            }}
        """)


class ProcessSelectorCard(CardFrame):
    process_selected = pyqtSignal(WindowInfo)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._windows = []
        self._selected_window = None
        self._setup_ui()
        self._refresh_windows()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QHBoxLayout()
        title = QLabel("Выберите процесс")
        title.setStyleSheet(f"color: {COLORS.text_primary}; font-size: 18px; font-weight: bold;")
        header.addWidget(title)
        
        refresh_btn = OvalButton("Обновить", gradient_type="secondary")
        refresh_btn.setFixedSize(120, 45)
        refresh_btn.clicked.connect(self._refresh_windows)
        header.addStretch()
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        self.search_input = SearchInput("Поиск...")
        self.search_input.textChanged.connect(self._filter_windows)
        layout.addWidget(self.search_input)
        
        self.list_widget = ModernListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
    def _refresh_windows(self):
        wm = WindowManager()
        self._windows = wm.get_windows()
        self._filter_windows()
        
    def _filter_windows(self, query=""):
        self.list_widget.clear()
        search_term = query.lower() if query else ""
        
        for window in self._windows:
            if not search_term or search_term in window.title.lower():
                item = QListWidgetItem(window.title[:50])
                item.setData(Qt.UserRole, window)
                self.list_widget.addItem(item)
            
    def _on_item_clicked(self, item):
        window = item.data(Qt.UserRole)
        if window:
            self._selected_window = window
            self.process_selected.emit(window)


class PositionSizeCard(CardFrame):
    values_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Положение и размер")
        title.setStyleSheet(f"color: {COLORS.text_primary}; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        grid = QGridLayout()
        self.x_spin = self._create_spinbox(0, 10000, 0)
        self.y_spin = self._create_spinbox(0, 10000, 0)
        self.width_spin = self._create_spinbox(1, 10000, 800)
        self.height_spin = self._create_spinbox(1, 10000, 600)
        
        for spin in [self.x_spin, self.y_spin, self.width_spin, self.height_spin]:
            spin.valueChanged.connect(self.values_changed.emit)
        
        grid.addWidget(QLabel("X:"), 0, 0)
        grid.addWidget(self.x_spin, 0, 1)
        grid.addWidget(QLabel("Y:"), 0, 2)
        grid.addWidget(self.y_spin, 0, 3)
        grid.addWidget(QLabel("W:"), 1, 0)
        grid.addWidget(self.width_spin, 1, 1)
        grid.addWidget(QLabel("H:"), 1, 2)
        grid.addWidget(self.height_spin, 1, 3)
        
        layout.addLayout(grid)
        layout.addStretch()
        
    def _create_spinbox(self, min_val, max_val, value):
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(value)
        spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS.bg_dark};
                border: 2px solid {COLORS.border_light};
                border-radius: 12px;
                padding: 10px;
                color: {COLORS.text_primary};
            }}
        """)
        return spin
        
    def get_values(self):
        return (self.x_spin.value(), self.y_spin.value(), 
                self.width_spin.value(), self.height_spin.value())
        
    def set_from_window(self, window):
        self.x_spin.setValue(window.x)
        self.y_spin.setValue(window.y)
        self.width_spin.setValue(window.width)
        self.height_spin.setValue(window.height)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automizer")
        self.setMinimumSize(1200, 800)
        
        self.normalizer = ProcessNormalizer()
        self.storage = PresetStorage()
        self._selected_window = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("Automizer")
        header.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {COLORS.text_primary};")
        layout.addWidget(header)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        tab1 = self._create_process_tab()
        self.tabs.addTab(tab1, "Процессы")
        
        for name, text in [("p", "Пресеты"), ("s", "Скриншоты")]:
            widget = QWidget()
            w_layout = QVBoxLayout(widget)
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"font-size: 20px; color: {COLORS.text_primary};")
            w_layout.addWidget(label)
            self.tabs.addTab(widget, name)
        
    def _create_process_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(20)
        
        left = ProcessSelectorCard()
        left.process_selected.connect(self._on_process_selected)
        
        right = QWidget()
        right_layout = QVBoxLayout(right)
        
        self.position_card = PositionSizeCard()
        
        normalize_btn = OvalButton("Нормализовать", gradient_type="success")
        normalize_btn.setMinimumHeight(50)
        normalize_btn.clicked.connect(self._normalize_window)
        
        right_layout.addWidget(self.position_card)
        right_layout.addWidget(normalize_btn)
        right_layout.addStretch()
        
        layout.addWidget(left, stretch=2)
        layout.addWidget(right, stretch=1)
        
        return widget
        
    def _on_process_selected(self, window):
        self._selected_window = window
        self.position_card.set_from_window(window)
        
    def _normalize_window(self):
        if not self._selected_window:
            QMessageBox.warning(self, "Warning", "Выберите окно")
            return
        try:
            x, y, w, h = self.position_card.get_values()
            if self.normalizer.normalize_window(self._selected_window.window_id, x, y, w, h):
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
