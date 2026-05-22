"""
Главное окно приложения Automizer.
Современный красивый резиновый интерфейс с 4 вкладками:
1. Выбор процесса - выбор окна и настройка позиции/размеров
2. Пресеты процессов - управление пресетами нормализации
3. Скриншоты - управление созданными скриншотами
4. Пресеты скриншотов - управление пресетами скриншотов и быстрый захват
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QScrollArea, QGridLayout, QSpacerItem,
    QSizePolicy, QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QFormLayout, QSpinBox, QComboBox, QGraphicsDropShadowEffect,
    QPropertyAnimation, QEasingCurve
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, pyqtProperty, QVariantAnimation
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QAction, QCursor

from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.window_manager import WindowManager, WindowInfo
from src.storage import PresetStorage
from src.screenshot import ScreenshotManager, ScreenshotInfo
from src.screenshot.presets import ScreenshotPresetStorage, ScreenshotPreset


class ModernStyle:
    """Современная темная цветовая схема."""
    
    # Цвета
    BG_PRIMARY = "#1e1e2e"      # Основной фон
    BG_SECONDARY = "#2a2a3e"    # Фон элементов
    BG_HOVER = "#3a3a5e"        # Фон при наведении
    TEXT_PRIMARY = "#ffffff"    # Основной текст
    TEXT_SECONDARY = "#a0a0b0"  # Вторичный текст
    ACCENT = "#7f8af4"          # Акцентный цвет (фиолетовый)
    ACCENT_HOVER = "#9aa0f4"    # Акцент при наведении
    SUCCESS = "#4ade80"         # Зеленый
    WARNING = "#fbbf24"         # Желтый
    DANGER = "#f87171"          # Красный
    BORDER = "#3a3a5e"          # Границы
    
    # Размеры
    BORDER_RADIUS = 12
    PADDING = 16
    SPACING = 12


def apply_modern_style(widget):
    """Применяет современный стиль к виджету."""
    style = f"""
        QWidget {{
            background-color: {ModernStyle.BG_PRIMARY};
            color: {ModernStyle.TEXT_PRIMARY};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
        }}
        
        /* Боковая панель */
        QFrame#sidebar {{
            background-color: {ModernStyle.BG_SECONDARY};
            border-right: 1px solid {ModernStyle.BORDER};
        }}
        
        /* Кнопки навигации */
        QPushButton#navBtn {{
            background-color: transparent;
            color: {ModernStyle.TEXT_SECONDARY};
            border: none;
            border-radius: {ModernStyle.BORDER_RADIUS}px;
            padding: 16px 20px;
            text-align: left;
            font-weight: bold;
            font-size: 15px;
            margin: 4px 8px;
        }}
        
        QPushButton#navBtn:hover {{
            background-color: {ModernStyle.BG_HOVER};
            color: {ModernStyle.TEXT_PRIMARY};
        }}
        
        QPushButton#navBtn:checked {{
            background-color: {ModernStyle.ACCENT};
            color: {ModernStyle.TEXT_PRIMARY};
        }}
        
        QPushButton {{
            background-color: {ModernStyle.ACCENT};
            color: {ModernStyle.TEXT_PRIMARY};
            border: none;
            border-radius: {ModernStyle.BORDER_RADIUS}px;
            padding: 12px 24px;
            font-weight: bold;
            min-width: 100px;
        }}
        
        QPushButton:hover {{
            background-color: {ModernStyle.ACCENT_HOVER};
        }}
        
        QPushButton:pressed {{
            background-color: {ModernStyle.ACCENT};
        }}
        
        QPushButton:disabled {{
            background-color: {ModernStyle.BORDER};
            color: {ModernStyle.TEXT_SECONDARY};
        }}
        
        QPushButton#secondaryBtn {{
            background-color: transparent;
            border: 2px solid {ModernStyle.ACCENT};
            color: {ModernStyle.ACCENT};
        }}
        
        QPushButton#secondaryBtn:hover {{
            background-color: {ModernStyle.ACCENT};
            color: {ModernStyle.TEXT_PRIMARY};
        }}
        
        QPushButton#dangerBtn {{
            background-color: {ModernStyle.DANGER};
        }}
        
        QPushButton#dangerBtn:hover {{
            background-color: #ef4444;
        }}
        
        QPushButton#successBtn {{
            background-color: {ModernStyle.SUCCESS};
            color: #1e1e2e;
        }}
        
        QLineEdit, QSpinBox, QComboBox, QDoubleSpinBox {{
            background-color: {ModernStyle.BG_PRIMARY};
            border: 2px solid {ModernStyle.BORDER};
            border-radius: {ModernStyle.BORDER_RADIUS}px;
            padding: 10px 16px;
            color: {ModernStyle.TEXT_PRIMARY};
            selection-background-color: {ModernStyle.ACCENT};
        }}
        
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border-color: {ModernStyle.ACCENT};
        }}
        
        QTableWidget {{
            background-color: {ModernStyle.BG_PRIMARY};
            alternate-background-color: {ModernStyle.BG_SECONDARY};
            border: 2px solid {ModernStyle.BORDER};
            border-radius: {ModernStyle.BORDER_RADIUS}px;
            gridline-color: {ModernStyle.BORDER};
            selection-background-color: {ModernStyle.ACCENT};
        }}
        
        QTableWidget::item {{
            padding: 10px;
            border-bottom: 1px solid {ModernStyle.BORDER};
        }}
        
        QTableWidget::item:selected {{
            background-color: {ModernStyle.ACCENT};
        }}
        
        QHeaderView::section {{
            background-color: {ModernStyle.BG_SECONDARY};
            color: {ModernStyle.TEXT_SECONDARY};
            padding: 12px;
            border: none;
            border-bottom: 2px solid {ModernStyle.ACCENT};
            font-weight: bold;
        }}
        
        QScrollBar:vertical {{
            background-color: {ModernStyle.BG_PRIMARY};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {ModernStyle.BORDER};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {ModernStyle.ACCENT};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {ModernStyle.BG_PRIMARY};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {ModernStyle.BORDER};
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {ModernStyle.ACCENT};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        QLabel#titleLabel {{
            font-size: 24px;
            font-weight: bold;
            color: {ModernStyle.TEXT_PRIMARY};
            margin-bottom: 20px;
        }}
        
        QLabel#sectionTitle {{
            font-size: 18px;
            font-weight: bold;
            color: {ModernStyle.ACCENT};
            margin-top: 10px;
            margin-bottom: 10px;
        }}
        
        QFrame#card {{
            background-color: {ModernStyle.BG_SECONDARY};
            border-radius: {ModernStyle.BORDER_RADIUS}px;
            padding: 16px;
        }}
        
        QGroupBox {{
            border: 2px solid {ModernStyle.BORDER};
            border-radius: {ModernStyle.BORDER_RADIUS}px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
            color: {ModernStyle.TEXT_SECONDARY};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
            color: {ModernStyle.ACCENT};
        }}
        
        QMessageBox {{
            background-color: {ModernStyle.BG_SECONDARY};
        }}
        
        QMessageBox QLabel {{
            color: {ModernStyle.TEXT_PRIMARY};
        }}
        
        QMessageBox QPushButton {{
            min-width: 80px;
        }}
    """
    widget.setStyleSheet(style)


class SidebarButton(QPushButton):
    """Кнопка боковой панели с анимацией."""
    
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(f"{icon}  {text}", parent)
        self.setObjectName("navBtn")
        self.setCheckable(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(50)


class WindowSelectionWidget(QWidget):
    """Виджет выбора и настройки окна (вкладка 1)."""
    
    window_selected = pyqtSignal(WindowInfo)
    
    def __init__(self, normalizer: ProcessNormalizer):
        super().__init__()
        self.normalizer = normalizer
        self.current_window: WindowInfo | None = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING)
        layout.setContentsMargins(ModernStyle.PADDING, ModernStyle.PADDING, 
                                   ModernStyle.PADDING, ModernStyle.PADDING)
        
        # Заголовок
        title = QLabel("🪟 Выбор и настройка окна")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Поиск окон
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по названию окна...")
        self.search_input.textChanged.connect(self._search_windows)
        search_layout.addWidget(self.search_input)
        
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self._load_windows)
        search_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Таблица окон
        self.windows_table = QTableWidget()
        self.windows_table.setColumnCount(4)
        self.windows_table.setHorizontalHeaderLabels([
            "Заголовок окна", "Позиция (X, Y)", "Размер (ШxВ)", "PID"
        ])
        self.windows_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.windows_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.windows_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.windows_table.itemSelectionChanged.connect(self._on_window_selected)
        layout.addWidget(self.windows_table)
        
        # Панель настроек
        settings_card = QFrame()
        settings_card.setObjectName("card")
        settings_layout = QVBoxLayout(settings_card)
        
        settings_title = QLabel("⚙️ Настройка позиции и размеров")
        settings_title.setObjectName("sectionTitle")
        settings_layout.addWidget(settings_title)
        
        # Поля ввода координат
        coords_layout = QGridLayout()
        coords_layout.setSpacing(12)
        
        self.x_input = QSpinBox()
        self.x_input.setRange(-10000, 10000)
        self.y_input = QSpinBox()
        self.y_input.setRange(-10000, 10000)
        self.width_input = QSpinBox()
        self.width_input.setRange(100, 10000)
        self.height_input = QSpinBox()
        self.height_input.setRange(100, 10000)
        
        coords_layout.addWidget(QLabel("X:"), 0, 0)
        coords_layout.addWidget(self.x_input, 0, 1)
        coords_layout.addWidget(QLabel("Y:"), 0, 2)
        coords_layout.addWidget(self.y_input, 0, 3)
        coords_layout.addWidget(QLabel("Ширина:"), 1, 0)
        coords_layout.addWidget(self.width_input, 1, 1)
        coords_layout.addWidget(QLabel("Высота:"), 1, 2)
        coords_layout.addWidget(self.height_input, 1, 3)
        
        settings_layout.addLayout(coords_layout)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.apply_btn = QPushButton("✓ Применить к окну")
        self.apply_btn.setObjectName("successBtn")
        self.apply_btn.clicked.connect(self._apply_to_window)
        self.apply_btn.setEnabled(False)
        buttons_layout.addWidget(self.apply_btn)
        
        self.focus_btn = QPushButton("🎯 Фокус")
        self.focus_btn.setObjectName("secondaryBtn")
        self.focus_btn.clicked.connect(self._focus_window)
        self.focus_btn.setEnabled(False)
        buttons_layout.addWidget(self.focus_btn)
        
        buttons_layout.addStretch()
        settings_layout.addLayout(buttons_layout)
        
        layout.addWidget(settings_card)
        
        # Загружаем окна
        self._load_windows()
    
    def _load_windows(self):
        """Загружает список окон."""
        self.windows_table.setRowCount(0)
        windows = self.normalizer.search_windows("")
        
        for window in windows:
            row = self.windows_table.rowCount()
            self.windows_table.insertRow(row)
            
            self.windows_table.setItem(row, 0, QTableWidgetItem(window.title))
            self.windows_table.setItem(row, 1, QTableWidgetItem(f"{window.x}, {window.y}"))
            self.windows_table.setItem(row, 2, QTableWidgetItem(f"{window.width} x {window.height}"))
            self.windows_table.setItem(row, 3, QTableWidgetItem(str(window.pid or "N/A")))
    
    def _search_windows(self, text: str):
        """Ищет окна по запросу."""
        self.windows_table.setRowCount(0)
        windows = self.normalizer.search_windows(text)
        
        for window in windows:
            row = self.windows_table.rowCount()
            self.windows_table.insertRow(row)
            
            self.windows_table.setItem(row, 0, QTableWidgetItem(window.title))
            self.windows_table.setItem(row, 1, QTableWidgetItem(f"{window.x}, {window.y}"))
            self.windows_table.setItem(row, 2, QTableWidgetItem(f"{window.width} x {window.height}"))
            self.windows_table.setItem(row, 3, QTableWidgetItem(str(window.pid or "N/A")))
    
    def _on_window_selected(self):
        """Обработчик выбора окна."""
        selected_rows = self.windows_table.selectedItems()
        if not selected_rows:
            self.current_window = None
            self.apply_btn.setEnabled(False)
            self.focus_btn.setEnabled(False)
            return
        
        row = selected_rows[0].row()
        window_id = int(self.windows_table.item(row, 0).data(Qt.ItemDataRole.UserRole) or 0)
        
        # Находим окно по заголовку (упрощенно)
        title = self.windows_table.item(row, 0).text()
        windows = self.normalizer.search_windows(title)
        if windows:
            self.current_window = windows[0]
            self.x_input.setValue(self.current_window.x)
            self.y_input.setValue(self.current_window.y)
            self.width_input.setValue(self.current_window.width)
            self.height_input.setValue(self.current_window.height)
            self.apply_btn.setEnabled(True)
            self.focus_btn.setEnabled(True)
            self.window_selected.emit(self.current_window)
    
    def _apply_preset(self, preset_name: str):
        """Применяет пресет позиционирования."""
        if not self.current_window:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите окно!")
            return
        
        # Получаем размер экрана (упрощенно - берем текущее окно как参考)
        screen_width = 1920  # Можно улучшить через QScreen
        screen_height = 1080
        
        presets = {
            "half_left": (0, 0, screen_width // 2, screen_height),
            "half_right": (screen_width // 2, 0, screen_width // 2, screen_height),
            "quarter_tl": (0, 0, screen_width // 2, screen_height // 2),
            "quarter_tr": (screen_width // 2, 0, screen_width // 2, screen_height // 2),
            "quarter_bl": (0, screen_height // 2, screen_width // 2, screen_height // 2),
            "quarter_br": (screen_width // 2, screen_height // 2, screen_width // 2, screen_height // 2),
            "fullscreen": (0, 0, screen_width, screen_height),
        }
        
        if preset_name in presets:
            x, y, w, h = presets[preset_name]
            self.x_input.setValue(x)
            self.y_input.setValue(y)
            self.width_input.setValue(w)
            self.height_input.setValue(h)
    
    def _apply_to_window(self):
        """Применяет настройки к окну."""
        if not self.current_window:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите окно!")
            return
        
        success = self.normalizer.normalize_window(
            window_id=self.current_window.window_id,
            x=self.x_input.value(),
            y=self.y_input.value(),
            width=self.width_input.value(),
            height=self.height_input.value(),
        )
        
        if success:
            QMessageBox.information(self, "Успех", "Окно успешно нормализовано!")
            self._load_windows()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось изменить окно!")
    
    def _focus_window(self):
        """Фокусируется на окне."""
        if not self.current_window:
            return
        
        self.normalizer.window_manager.focus_window(self.current_window.window_id)


class ProcessPresetsWidget(QWidget):
    """Виджет управления пресетами процессов (вкладка 2)."""
    
    def __init__(self, storage: PresetStorage, normalizer: ProcessNormalizer):
        super().__init__()
        self.storage = storage
        self.normalizer = normalizer
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING)
        layout.setContentsMargins(ModernStyle.PADDING, ModernStyle.PADDING,
                                   ModernStyle.PADDING, ModernStyle.PADDING)
        
        # Заголовок
        title = QLabel("📋 Пресеты процессов")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск пресетов...")
        self.search_input.textChanged.connect(self._search_presets)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Таблица пресетов
        self.presets_table = QTableWidget()
        self.presets_table.setColumnCount(5)
        self.presets_table.setHorizontalHeaderLabels([
            "Имя", "Процесс", "Позиция", "Размер", "Описание"
        ])
        self.presets_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.presets_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.presets_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        layout.addWidget(self.presets_table)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.clicked.connect(self._add_preset)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setObjectName("secondaryBtn")
        self.edit_btn.clicked.connect(self._edit_preset)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._delete_preset)
        buttons_layout.addWidget(self.delete_btn)
        
        self.apply_preset_btn = QPushButton("▶️ Применить")
        self.apply_preset_btn.setObjectName("successBtn")
        self.apply_preset_btn.clicked.connect(self._apply_preset)
        buttons_layout.addWidget(self.apply_preset_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Загружаем пресеты
        self._load_presets()
    
    def _load_presets(self):
        """Загружает пресеты в таблицу."""
        self.presets_table.setRowCount(0)
        presets = self.storage.get_all_presets()
        
        for preset in presets:
            row = self.presets_table.rowCount()
            self.presets_table.insertRow(row)
            
            item = QTableWidgetItem(preset.name)
            item.setData(Qt.ItemDataRole.UserRole, preset.id)
            self.presets_table.setItem(row, 0, item)
            
            self.presets_table.setItem(row, 1, QTableWidgetItem(preset.process_name))
            self.presets_table.setItem(row, 2, QTableWidgetItem(f"{preset.x}, {preset.y}"))
            self.presets_table.setItem(row, 3, QTableWidgetItem(f"{preset.width} x {preset.height}"))
            self.presets_table.setItem(row, 4, QTableWidgetItem(preset.description))
    
    def _search_presets(self, text: str):
        """Ищет пресеты."""
        self.presets_table.setRowCount(0)
        presets = self.storage.search_presets(text)
        
        for preset in presets:
            row = self.presets_table.rowCount()
            self.presets_table.insertRow(row)
            
            item = QTableWidgetItem(preset.name)
            item.setData(Qt.ItemDataRole.UserRole, preset.id)
            self.presets_table.setItem(row, 0, item)
            
            self.presets_table.setItem(row, 1, QTableWidgetItem(preset.process_name))
            self.presets_table.setItem(row, 2, QTableWidgetItem(f"{preset.x}, {preset.y}"))
            self.presets_table.setItem(row, 3, QTableWidgetItem(f"{preset.width} x {preset.height}"))
            self.presets_table.setItem(row, 4, QTableWidgetItem(preset.description))
    
    def _get_selected_preset(self) -> NormalizationPreset | None:
        """Получает выбранный пресет."""
        selected_rows = self.presets_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        preset_id = self.presets_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return self.storage.get_preset(preset_id)
    
    def _add_preset(self):
        """Добавляет новый пресет."""
        dialog = PresetDialog(self, "Добавление пресета")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                self.storage.add_preset(**data)
                self._load_presets()
                QMessageBox.information(self, "Успех", "Пресет добавлен!")
            except ValueError as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def _edit_preset(self):
        """Редактирует пресет."""
        preset = self._get_selected_preset()
        if not preset:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        dialog = PresetDialog(self, "Редактирование пресета", preset)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.storage.update_preset(preset_id=preset.id, **data)
            self._load_presets()
            QMessageBox.information(self, "Успех", "Пресет обновлен!")
    
    def _delete_preset(self):
        """Удаляет пресет."""
        preset = self._get_selected_preset()
        if not preset:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить пресет '{preset.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.remove_preset(preset.id)
            self._load_presets()
    
    def _apply_preset(self):
        """Применяет пресет к окну."""
        preset = self._get_selected_preset()
        if not preset:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        success = self.normalizer.apply_preset(preset)
        if success:
            QMessageBox.information(self, "Успех", f"Пресет '{preset.name}' применен!")
        else:
            QMessageBox.critical(self, "Ошибка", "Окно не найдено или не удалось применить пресет!")


class PresetDialog(QDialog):
    """Диалог для создания/редактирования пресета."""
    
    def __init__(self, parent=None, title: str = "", preset: NormalizationPreset | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.preset = preset
        self._setup_ui()
        
        if preset:
            self._fill_data(preset)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Chrome слева")
        form.addRow("Имя:", self.name_input)
        
        self.process_input = QLineEdit()
        self.process_input.setPlaceholderText("Например: chrome")
        form.addRow("Процесс:", self.process_input)
        
        self.x_input = QSpinBox()
        self.x_input.setRange(-10000, 10000)
        form.addRow("X:", self.x_input)
        
        self.y_input = QSpinBox()
        self.y_input.setRange(-10000, 10000)
        form.addRow("Y:", self.y_input)
        
        self.width_input = QSpinBox()
        self.width_input.setRange(100, 10000)
        form.addRow("Ширина:", self.width_input)
        
        self.height_input = QSpinBox()
        self.height_input.setRange(100, 10000)
        form.addRow("Высота:", self.height_input)
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Описание пресета")
        form.addRow("Описание:", self.desc_input)
        
        layout.addLayout(form)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _fill_data(self, preset: NormalizationPreset):
        """Заполняет форму данными пресета."""
        self.name_input.setText(preset.name)
        self.process_input.setText(preset.process_name)
        self.x_input.setValue(preset.x)
        self.y_input.setValue(preset.y)
        self.width_input.setValue(preset.width)
        self.height_input.setValue(preset.height)
        self.desc_input.setText(preset.description)
    
    def get_data(self) -> dict:
        """Возвращает данные из формы."""
        return {
            "name": self.name_input.text(),
            "process_name": self.process_input.text(),
            "x": self.x_input.value(),
            "y": self.y_input.value(),
            "width": self.width_input.value(),
            "height": self.height_input.value(),
            "description": self.desc_input.text(),
        }


class ScreenshotsWidget(QWidget):
    """Виджет управления скриншотами (вкладка 3)."""
    
    def __init__(self, screenshot_manager: ScreenshotManager):
        super().__init__()
        self.screenshot_manager = screenshot_manager
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING)
        layout.setContentsMargins(ModernStyle.PADDING, ModernStyle.PADDING,
                                   ModernStyle.PADDING, ModernStyle.PADDING)
        
        # Заголовок
        title = QLabel("📸 Скриншоты")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск скриншотов...")
        self.search_input.textChanged.connect(self._search_screenshots)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Таблица скриншотов
        self.screenshots_table = QTableWidget()
        self.screenshots_table.setColumnCount(4)
        self.screenshots_table.setHorizontalHeaderLabels([
            "ID", "Описание", "Размер области", "Дата создания"
        ])
        self.screenshots_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.screenshots_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.screenshots_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.screenshots_table.cellDoubleClicked.connect(self._open_screenshot)
        layout.addWidget(self.screenshots_table)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.open_folder_btn = QPushButton("📁 Открыть папку")
        self.open_folder_btn.setObjectName("secondaryBtn")
        self.open_folder_btn.clicked.connect(self._open_folder)
        buttons_layout.addWidget(self.open_folder_btn)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._delete_screenshot)
        buttons_layout.addWidget(self.delete_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Загружаем скриншоты
        self._load_screenshots()
    
    def _load_screenshots(self):
        """Загружает скриншоты в таблицу."""
        self.screenshots_table.setRowCount(0)
        screenshots = self.screenshot_manager.get_all_screenshots()
        
        for shot in screenshots:
            row = self.screenshots_table.rowCount()
            self.screenshots_table.insertRow(row)
            
            item = QTableWidgetItem(shot.id)
            item.setData(Qt.ItemDataRole.UserRole, shot.id)
            self.screenshots_table.setItem(row, 0, item)
            
            self.screenshots_table.setItem(row, 1, QTableWidgetItem(shot.description or "—"))
            self.screenshots_table.setItem(row, 2, QTableWidgetItem(f"{shot.width} x {shot.height}"))
            self.screenshots_table.setItem(row, 3, QTableWidgetItem(
                shot.created_at.strftime("%d.%m.%Y %H:%M")
            ))
    
    def _search_screenshots(self, text: str):
        """Ищет скриншоты."""
        self.screenshots_table.setRowCount(0)
        screenshots = self.screenshot_manager.search_screenshots(text)
        
        for shot in screenshots:
            row = self.screenshots_table.rowCount()
            self.screenshots_table.insertRow(row)
            
            item = QTableWidgetItem(shot.id)
            item.setData(Qt.ItemDataRole.UserRole, shot.id)
            self.screenshots_table.setItem(row, 0, item)
            
            self.screenshots_table.setItem(row, 1, QTableWidgetItem(shot.description or "—"))
            self.screenshots_table.setItem(row, 2, QTableWidgetItem(f"{shot.width} x {shot.height}"))
            self.screenshots_table.setItem(row, 3, QTableWidgetItem(
                shot.created_at.strftime("%d.%m.%Y %H:%M")
            ))
    
    def _get_selected_screenshot(self) -> ScreenshotInfo | None:
        """Получает выбранный скриншот."""
        selected_rows = self.screenshots_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        screenshot_id = self.screenshots_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return self.screenshot_manager.get_screenshot(screenshot_id)
    
    def _open_screenshot(self, row: int, column: int):
        """Открывает скриншот."""
        screenshot = self._get_selected_screenshot()
        if screenshot and screenshot.path.exists():
            import subprocess
            subprocess.Popen(["xdg-open", str(screenshot.path)])
    
    def _open_folder(self):
        """Открывает папку со скриншотами."""
        import subprocess
        subprocess.Popen(["xdg-open", str(self.screenshot_manager.storage_path)])
    
    def _delete_screenshot(self):
        """Удаляет скриншот."""
        screenshot = self._get_selected_screenshot()
        if not screenshot:
            QMessageBox.warning(self, "Предупреждение", "Выберите скриншот!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить скриншот '{screenshot.id}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.screenshot_manager.remove_screenshot(screenshot.id)
            self._load_screenshots()


class ScreenshotPresetsWidget(QWidget):
    """Виджет управления пресетами скриншотов (вкладка 4)."""
    
    def __init__(self, 
                 preset_storage: ScreenshotPresetStorage,
                 process_storage: PresetStorage,
                 screenshot_manager: ScreenshotManager,
                 normalizer: ProcessNormalizer):
        super().__init__()
        self.preset_storage = preset_storage
        self.process_storage = process_storage
        self.screenshot_manager = screenshot_manager
        self.normalizer = normalizer
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING)
        layout.setContentsMargins(ModernStyle.PADDING, ModernStyle.PADDING,
                                   ModernStyle.PADDING, ModernStyle.PADDING)
        
        # Заголовок
        title = QLabel("🎬 Пресеты скриншотов и быстрый захват")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск пресетов...")
        self.search_input.textChanged.connect(self._search_presets)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Таблица пресетов
        self.presets_table = QTableWidget()
        self.presets_table.setColumnCount(6)
        self.presets_table.setHorizontalHeaderLabels([
            "Имя", "Пресет процесса", "Позиция", "Размер", "Путь", "Описание"
        ])
        self.presets_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.presets_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.presets_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        layout.addWidget(self.presets_table)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.clicked.connect(self._add_preset)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setObjectName("secondaryBtn")
        self.edit_btn.clicked.connect(self._edit_preset)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._delete_preset)
        buttons_layout.addWidget(self.delete_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Секция быстрого захвата
        capture_card = QFrame()
        capture_card.setObjectName("card")
        capture_layout = QVBoxLayout(capture_card)
        
        capture_title = QLabel("⚡ Быстрый захват")
        capture_title.setObjectName("sectionTitle")
        capture_layout.addWidget(capture_title)
        
        # Выбор пресетов
        select_layout = QHBoxLayout()
        select_layout.setSpacing(16)
        
        self.process_preset_combo = QComboBox()
        self.process_preset_combo.addItem("Выберите пресет процесса...", "")
        self._update_process_presets()
        select_layout.addWidget(QLabel("Пресет процесса:"))
        select_layout.addWidget(self.process_preset_combo)
        
        self.screenshot_preset_combo = QComboBox()
        self.screenshot_preset_combo.addItem("Выберите пресет скриншота...", "")
        self._update_screenshot_presets()
        select_layout.addWidget(QLabel("Пресет скриншота:"))
        select_layout.addWidget(self.screenshot_preset_combo)
        
        capture_layout.addLayout(select_layout)
        
        # Кнопки захвата
        capture_buttons = QHBoxLayout()
        capture_buttons.setSpacing(12)
        
        self.capture_only_btn = QPushButton("📸 Только скриншот")
        self.capture_only_btn.setObjectName("secondaryBtn")
        self.capture_only_btn.clicked.connect(self._capture_screenshot_only)
        capture_buttons.addWidget(self.capture_only_btn)
        
        self.full_capture_btn = QPushButton("🎯 Полный захват (нормализация + скриншот)")
        self.full_capture_btn.setObjectName("successBtn")
        self.full_capture_btn.clicked.connect(self._full_capture)
        capture_buttons.addWidget(self.full_capture_btn)
        
        capture_buttons.addStretch()
        capture_layout.addLayout(capture_buttons)
        
        layout.addWidget(capture_card)
        
        # Загружаем пресеты
        self._load_presets()
    
    def _update_process_presets(self):
        """Обновляет список пресетов процессов."""
        self.process_preset_combo.clear()
        self.process_preset_combo.addItem("Выберите пресет процесса...", "")
        
        for preset in self.process_storage.get_all_presets():
            self.process_preset_combo.addItem(preset.name, preset.id)
    
    def _update_screenshot_presets(self):
        """Обновляет список пресетов скриншотов."""
        self.screenshot_preset_combo.clear()
        self.screenshot_preset_combo.addItem("Выберите пресет скриншота...", "")
        
        for preset in self.preset_storage.get_all_presets():
            self.screenshot_preset_combo.addItem(preset.name, preset.id)
    
    def _load_presets(self):
        """Загружает пресеты в таблицу."""
        self.presets_table.setRowCount(0)
        presets = self.preset_storage.get_all_presets()
        
        for preset in presets:
            row = self.presets_table.rowCount()
            self.presets_table.insertRow(row)
            
            item = QTableWidgetItem(preset.name)
            item.setData(Qt.ItemDataRole.UserRole, preset.id)
            self.presets_table.setItem(row, 0, item)
            
            self.presets_table.setItem(row, 1, QTableWidgetItem(preset.process_preset_id))
            self.presets_table.setItem(row, 2, QTableWidgetItem(f"{preset.x}, {preset.y}"))
            self.presets_table.setItem(row, 3, QTableWidgetItem(f"{preset.width} x {preset.height}"))
            self.presets_table.setItem(row, 4, QTableWidgetItem(preset.screenshot_path))
            self.presets_table.setItem(row, 5, QTableWidgetItem(preset.description))
    
    def _search_presets(self, text: str):
        """Ищет пресеты."""
        self.presets_table.setRowCount(0)
        presets = self.preset_storage.search_presets(text)
        
        for preset in presets:
            row = self.presets_table.rowCount()
            self.presets_table.insertRow(row)
            
            item = QTableWidgetItem(preset.name)
            item.setData(Qt.ItemDataRole.UserRole, preset.id)
            self.presets_table.setItem(row, 0, item)
            
            self.presets_table.setItem(row, 1, QTableWidgetItem(preset.process_preset_id))
            self.presets_table.setItem(row, 2, QTableWidgetItem(f"{preset.x}, {preset.y}"))
            self.presets_table.setItem(row, 3, QTableWidgetItem(f"{preset.width} x {preset.height}"))
            self.presets_table.setItem(row, 4, QTableWidgetItem(preset.screenshot_path))
            self.presets_table.setItem(row, 5, QTableWidgetItem(preset.description))
    
    def _get_selected_preset(self) -> ScreenshotPreset | None:
        """Получает выбранный пресет."""
        selected_rows = self.presets_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        preset_id = self.presets_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return self.preset_storage.get_preset(preset_id)
    
    def _add_preset(self):
        """Добавляет новый пресет скриншота."""
        dialog = ScreenshotPresetDialog(
            self, "Добавление пресета скриншота", self.process_storage
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                self.preset_storage.add_preset(**data)
                self._load_presets()
                self._update_screenshot_presets()
                QMessageBox.information(self, "Успех", "Пресет добавлен!")
            except ValueError as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def _edit_preset(self):
        """Редактирует пресет."""
        preset = self._get_selected_preset()
        if not preset:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        dialog = ScreenshotPresetDialog(
            self, "Редактирование пресета скриншота", self.process_storage, preset
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.preset_storage.update_preset(preset_id=preset.id, **data)
            self._load_presets()
            self._update_screenshot_presets()
            QMessageBox.information(self, "Успех", "Пресет обновлен!")
    
    def _delete_preset(self):
        """Удаляет пресет."""
        preset = self._get_selected_preset()
        if not preset:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить пресет '{preset.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.preset_storage.remove_preset(preset.id)
            self._load_presets()
            self._update_screenshot_presets()
    
    def _capture_screenshot_only(self):
        """Создает скриншот только по пресету."""
        preset_id = self.screenshot_preset_combo.currentData()
        if not preset_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет скриншота!")
            return
        
        preset = self.preset_storage.get_preset(preset_id)
        if not preset:
            return
        
        self.screenshot_manager.capture(
            x=preset.x,
            y=preset.y,
            width=preset.width,
            height=preset.height,
            description=f"Скриншот по пресету '{preset.name}'",
        )
        QMessageBox.information(self, "Успех", "Скриншот создан!")
    
    def _full_capture(self):
        """Выполняет полный захват: нормализация + скриншот."""
        process_preset_id = self.process_preset_combo.currentData()
        screenshot_preset_id = self.screenshot_preset_combo.currentData()
        
        if not process_preset_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет процесса!")
            return
        
        if not screenshot_preset_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет скриншота!")
            return
        
        # Применяем пресет процесса
        process_preset = self.process_storage.get_preset(process_preset_id)
        if not process_preset:
            QMessageBox.critical(self, "Ошибка", "Пресет процесса не найден!")
            return
        
        success = self.normalizer.apply_preset(process_preset)
        if not success:
            QMessageBox.critical(self, "Ошибка", "Не удалось применить пресет процесса!")
            return
        
        # Создаем скриншот
        screenshot_preset = self.preset_storage.get_preset(screenshot_preset_id)
        if not screenshot_preset:
            QMessageBox.critical(self, "Ошибка", "Пресет скриншота не найден!")
            return
        
        self.screenshot_manager.capture(
            x=screenshot_preset.x,
            y=screenshot_preset.y,
            width=screenshot_preset.width,
            height=screenshot_preset.height,
            description=f"Быстрый захват: {process_preset.name} + {screenshot_preset.name}",
        )
        
        QMessageBox.information(self, "Успех", "Полный захват выполнен!")


class ScreenshotPresetDialog(QDialog):
    """Диалог для создания/редактирования пресета скриншота."""
    
    def __init__(self, parent=None, title: str = "", 
                 process_storage: PresetStorage | None = None,
                 preset: ScreenshotPreset | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.process_storage = process_storage
        self.preset = preset
        self._setup_ui()
        
        if preset:
            self._fill_data(preset)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Скриншот Chrome")
        form.addRow("Имя:", self.name_input)
        
        # Выбор пресета процесса
        self.process_combo = QComboBox()
        self.process_combo.addItem("Выберите пресет...", "")
        if self.process_storage:
            for p in self.process_storage.get_all_presets():
                self.process_combo.addItem(p.name, p.id)
        form.addRow("Пресет процесса:", self.process_combo)
        
        self.x_input = QSpinBox()
        self.x_input.setRange(-10000, 10000)
        form.addRow("X:", self.x_input)
        
        self.y_input = QSpinBox()
        self.y_input.setRange(-10000, 10000)
        form.addRow("Y:", self.y_input)
        
        self.width_input = QSpinBox()
        self.width_input.setRange(100, 10000)
        form.addRow("Ширина:", self.width_input)
        
        self.height_input = QSpinBox()
        self.height_input.setRange(100, 10000)
        form.addRow("Высота:", self.height_input)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Путь сохранения (опционально)")
        form.addRow("Путь:", self.path_input)
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Описание")
        form.addRow("Описание:", self.desc_input)
        
        layout.addLayout(form)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _fill_data(self, preset: ScreenshotPreset):
        """Заполняет форму данными пресета."""
        self.name_input.setText(preset.name)
        self.process_combo.setCurrentText(preset.process_preset_id)
        self.x_input.setValue(preset.x)
        self.y_input.setValue(preset.y)
        self.width_input.setValue(preset.width)
        self.height_input.setValue(preset.height)
        self.path_input.setText(preset.screenshot_path)
        self.desc_input.setText(preset.description)
    
    def get_data(self) -> dict:
        """Возвращает данные из формы."""
        return {
            "name": self.name_input.text(),
            "process_preset_id": self.process_combo.currentData() or "default",
            "x": self.x_input.value(),
            "y": self.y_input.value(),
            "width": self.width_input.value(),
            "height": self.height_input.value(),
            "screenshot_path": self.path_input.text() or "presets/screenshots",
            "description": self.desc_input.text(),
        }


class MainWindow(QMainWindow):
    """Главное окно приложения Automizer с боковой панелью навигации."""
    
    def __init__(self):
        super().__init__()
        
        # Инициализируем компоненты
        self.window_manager = WindowManager()
        self.normalizer = ProcessNormalizer(self.window_manager)
        self.preset_storage = PresetStorage()
        self.screenshot_manager = ScreenshotManager()
        self.screenshot_preset_storage = ScreenshotPresetStorage()
        
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Настраивает пользовательский интерфейс с боковой панелью."""
        self.setWindowTitle("Automizer - Система нормализации окон")
        self.setMinimumSize(1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной макет горизонтальный
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Боковая панель
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(8)
        sidebar_layout.setContentsMargins(8, 20, 8, 20)
        
        # Заголовок приложения
        app_title = QLabel("🎯 Automizer")
        app_title.setObjectName("titleLabel")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_title.setStyleSheet("font-size: 28px; margin-bottom: 30px;")
        sidebar_layout.addWidget(app_title)
        
        sidebar_layout.addSpacing(20)
        
        # Кнопки навигации
        self.nav_buttons = []
        
        self.btn_window_selection = SidebarButton("🪟", "Выбор процесса")
        self.btn_window_selection.setChecked(True)
        sidebar_layout.addWidget(self.btn_window_selection)
        self.nav_buttons.append(self.btn_window_selection)
        
        self.btn_process_presets = SidebarButton("📋", "Пресеты процессов")
        sidebar_layout.addWidget(self.btn_process_presets)
        self.nav_buttons.append(self.btn_process_presets)
        
        self.btn_screenshots = SidebarButton("📸", "Скриншоты")
        sidebar_layout.addWidget(self.btn_screenshots)
        self.nav_buttons.append(self.btn_screenshots)
        
        self.btn_screenshot_presets = SidebarButton("🎬", "Пресеты скриншотов")
        sidebar_layout.addWidget(self.btn_screenshot_presets)
        self.nav_buttons.append(self.btn_screenshot_presets)
        
        sidebar_layout.addStretch()
        
        # Добавляем боковую панель в основной макет
        main_layout.addWidget(self.sidebar)
        
        # Область контента (стек виджетов)
        self.content_stack = QStackedWidget()
        self.content_stack.setContentsMargins(0, 0, 0, 0)
        
        # Вкладка 1: Выбор процесса
        self.window_selection = WindowSelectionWidget(self.normalizer)
        self.content_stack.addWidget(self.window_selection)
        
        # Вкладка 2: Пресеты процессов
        self.process_presets = ProcessPresetsWidget(
            self.preset_storage, self.normalizer
        )
        self.content_stack.addWidget(self.process_presets)
        
        # Вкладка 3: Скриншоты
        self.screenshots = ScreenshotsWidget(self.screenshot_manager)
        self.content_stack.addWidget(self.screenshots)
        
        # Вкладка 4: Пресеты скриншотов
        self.screenshot_presets = ScreenshotPresetsWidget(
            self.screenshot_preset_storage,
            self.preset_storage,
            self.screenshot_manager,
            self.normalizer
        )
        self.content_stack.addWidget(self.screenshot_presets)
        
        main_layout.addWidget(self.content_stack)
        
        # Подключаем кнопки навигации
        self.btn_window_selection.clicked.connect(lambda: self._switch_tab(0))
        self.btn_process_presets.clicked.connect(lambda: self._switch_tab(1))
        self.btn_screenshots.clicked.connect(lambda: self._switch_tab(2))
        self.btn_screenshot_presets.clicked.connect(lambda: self._switch_tab(3))
    
    def _switch_tab(self, index: int):
        """Переключает вкладку и обновляет состояние кнопок."""
        # Сбрасываем все кнопки
        for btn in self.nav_buttons:
            btn.setChecked(False)
        
        # Активируем нужную кнопку
        self.nav_buttons[index].setChecked(True)
        
        # Переключаем стек
        self.content_stack.setCurrentIndex(index)
    
    def _apply_styling(self):
        """Применяет современный стиль."""
        apply_modern_style(self)
