"""
Главное окно приложения Automizer.
Современный красивый резиновый интерфейс с 3 вкладками:
1. Выбор процесса - выбор окна и настройка позиции/размеров
2. Скриншоты - управление созданными скриншотами
3. Пресеты скриншотов - управление пресетами скриншотов и быстрый захват
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QScrollArea, QGridLayout, QSpacerItem,
    QSizePolicy, QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QFormLayout, QSpinBox, QComboBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, pyqtProperty, QVariantAnimation, QPropertyAnimation, QEasingCurve
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
        
        QLabel#fieldLabel {{
            font-size: 11px;
            color: {ModernStyle.TEXT_SECONDARY};
            font-weight: normal;
            margin: 0;
            padding: 2px 4px;
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
    
    def __init__(self, normalizer: ProcessNormalizer, storage: PresetStorage | None = None):
        super().__init__()
        self.normalizer = normalizer
        self.storage = storage or PresetStorage()
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
        coords_grid = QGridLayout()
        coords_grid.setSpacing(8)
        
        self.x_input = QSpinBox()
        self.x_input.setRange(-10000, 10000)
        self.y_input = QSpinBox()
        self.y_input.setRange(-10000, 10000)
        self.width_input = QSpinBox()
        self.width_input.setRange(100, 10000)
        self.height_input = QSpinBox()
        self.height_input.setRange(100, 10000)
        
        # Лейблы над полями (небольшие надписи)
        x_label = QLabel("X")
        x_label.setObjectName("fieldLabel")
        y_label = QLabel("Y")
        y_label.setObjectName("fieldLabel")
        width_label = QLabel("Ширина")
        width_label.setObjectName("fieldLabel")
        height_label = QLabel("Высота")
        height_label.setObjectName("fieldLabel")
        
        coords_grid.addWidget(x_label, 0, 0)
        coords_grid.addWidget(self.x_input, 1, 0)
        coords_grid.addWidget(y_label, 0, 1)
        coords_grid.addWidget(self.y_input, 1, 1)
        coords_grid.addWidget(width_label, 0, 2)
        coords_grid.addWidget(self.width_input, 1, 2)
        coords_grid.addWidget(height_label, 0, 3)
        coords_grid.addWidget(self.height_input, 1, 3)
        
        settings_layout.addLayout(coords_grid)
        
        # Кнопки действий - группа для работы с окном
        window_buttons_layout = QHBoxLayout()
        window_buttons_layout.setSpacing(12)
        
        self.apply_preset_btn = QPushButton("📋 Применить пресет")
        self.apply_preset_btn.setObjectName("secondaryBtn")
        self.apply_preset_btn.clicked.connect(self._apply_preset_from_selection)
        window_buttons_layout.addWidget(self.apply_preset_btn)
        
        self.apply_btn = QPushButton("✓ Применить к окну")
        self.apply_btn.setObjectName("successBtn")
        self.apply_btn.clicked.connect(self._apply_to_window)
        self.apply_btn.setEnabled(False)
        window_buttons_layout.addWidget(self.apply_btn)
        
        self.focus_btn = QPushButton("🎯 Фокус")
        self.focus_btn.setObjectName("secondaryBtn")
        self.focus_btn.clicked.connect(self._focus_window)
        self.focus_btn.setEnabled(False)
        window_buttons_layout.addWidget(self.focus_btn)
        
        window_buttons_layout.addStretch()
        settings_layout.addLayout(window_buttons_layout)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {ModernStyle.BORDER};")
        separator.setFixedHeight(2)
        settings_layout.addWidget(separator)
        
        # Кнопки действий - группа для работы с пресетами
        preset_buttons_layout = QHBoxLayout()
        preset_buttons_layout.setSpacing(12)
        
        self.save_preset_btn = QPushButton("💾 Сохранить как пресет")
        self.save_preset_btn.setObjectName("secondaryBtn")
        self.save_preset_btn.clicked.connect(self._save_as_preset)
        self.save_preset_btn.setEnabled(False)
        preset_buttons_layout.addWidget(self.save_preset_btn)
        
        self.delete_preset_btn = QPushButton("🗑️ Удалить пресет")
        self.delete_preset_btn.setObjectName("dangerBtn")
        self.delete_preset_btn.clicked.connect(self._delete_preset_dialog)
        preset_buttons_layout.addWidget(self.delete_preset_btn)
        
        preset_buttons_layout.addStretch()
        settings_layout.addLayout(preset_buttons_layout)
        
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
            self.save_preset_btn.setEnabled(False)
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
            self.save_preset_btn.setEnabled(True)
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
    
    def _save_as_preset(self):
        """Сохраняет текущие настройки как пресет."""
        if not self.current_window:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите окно!")
            return
        
        # Создаем диалог для ввода данных пресета
        dialog = PresetDialog(self, "💾 Сохранить пресет")
        
        # Предзаполняем X, Y, ширину и высоту из полей
        dialog.x_input.setValue(self.x_input.value())
        dialog.y_input.setValue(self.y_input.value())
        dialog.width_input.setValue(self.width_input.value())
        dialog.height_input.setValue(self.height_input.value())
        
        # Предзаполняем имя процесса из текущего окна
        if self.current_window and self.current_window.title:
            dialog.process_input.setText(self.current_window.title[:30])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            # Проверяем заполненность обязательных полей
            if not data["name"] or not data["process_name"]:
                QMessageBox.warning(self, "Предупреждение", 
                    "Имя и процесс являются обязательными полями!")
                return
            
            # Генерируем ID из имени
            preset_id = data["name"].lower().replace(" ", "_").replace("/", "_")
            
            try:
                self.storage.add_preset(
                    preset_id=preset_id,
                    name=data["name"],
                    process_name=data["process_name"],
                    x=data["x"],
                    y=data["y"],
                    width=data["width"],
                    height=data["height"],
                    description=data["description"],
                )
                QMessageBox.information(self, "Успех", 
                    f"Пресет '{data['name']}' успешно сохранен!")
            except ValueError as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def _apply_preset_from_selection(self):
        """Применяет пресет к выделенному процессу или просит выбрать."""
        # Проверяем, есть ли выделенное окно
        selected_rows = self.windows_table.selectedItems()
        
        if selected_rows:
            # Есть выделенное окно - ищем пресет по нему
            row = selected_rows[0].row()
            title = self.windows_table.item(row, 0).text()
            
            # Ищем пресеты для этого процесса
            matching_presets = []
            all_presets = self.storage.get_all_presets()
            
            for preset in all_presets:
                if preset.process_name.lower() in title.lower() or title.lower() in preset.process_name.lower():
                    matching_presets.append(preset)
            
            if len(matching_presets) == 0:
                QMessageBox.information(self, "Информация", 
                    f"Для процесса '{title}' не найдено пресетов.\n\n"
                    f"Вы можете сохранить текущие настройки как пресет, нажав '💾 Сохранить как пресет'.")
            elif len(matching_presets) == 1:
                # Найден один пресет - применяем сразу
                preset = matching_presets[0]
                self._apply_preset_values(preset, apply_immediately=True)
            else:
                # Найдено несколько пресетов - даем выбрать
                self._show_preset_selection_dialog(title, matching_presets)
        else:
            # Нет выделенного окна - просим выбрать процесс и пресет
            self._show_process_and_preset_dialog()
    
    def _apply_preset_values(self, preset: NormalizationPreset, apply_immediately: bool = True):
        """Устанавливает значения из пресета в поля ввода и применяет к окну."""
        self.x_input.setValue(preset.x)
        self.y_input.setValue(preset.y)
        self.width_input.setValue(preset.width)
        self.height_input.setValue(preset.height)
        
        # Если окно выбрано и нужно применить сразу - применяем
        if apply_immediately and self.current_window:
            self._apply_to_window()
    
    def _show_preset_selection_dialog(self, process_title: str, presets: list[NormalizationPreset]):
        """Показывает диалог выбора пресета при наличии нескольких вариантов."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите пресет")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel(f"Для процесса '{process_title}' найдено несколько пресетов:")
        layout.addWidget(label)
        
        # Список пресетов
        preset_list = QTableWidget()
        preset_list.setColumnCount(3)
        preset_list.setHorizontalHeaderLabels(["Имя", "Процесс", "Описание"])
        preset_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        preset_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        preset_list.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        for preset in presets:
            row = preset_list.rowCount()
            preset_list.insertRow(row)
            preset_list.setItem(row, 0, QTableWidgetItem(preset.name))
            preset_list.setItem(row, 1, QTableWidgetItem(preset.process_name))
            preset_list.setItem(row, 2, QTableWidgetItem(preset.description))
        
        layout.addWidget(preset_list)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        apply_btn = QPushButton("✓ Применить")
        apply_btn.clicked.connect(lambda: self._on_preset_selected(dialog, preset_list, presets))
        buttons_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec()
    
    def _on_preset_selected(self, dialog: QDialog, preset_list: QTableWidget, presets: list[NormalizationPreset]):
        """Обработчик выбора пресета из списка."""
        selected_rows = preset_list.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        row = selected_rows[0].row()
        preset = presets[row]
        self._apply_preset_values(preset, apply_immediately=True)
        dialog.accept()
    
    def _show_process_and_preset_dialog(self):
        """Показывает диалог выбора процесса и пресета когда нет выделения."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите процесс и пресет")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        # Верхняя часть - выбор процесса
        process_label = QLabel("🔍 Выберите процесс:")
        layout.addWidget(process_label)
        
        process_search = QLineEdit()
        process_search.setPlaceholderText("Поиск процесса...")
        layout.addWidget(process_search)
        
        process_list = QTableWidget()
        process_list.setColumnCount(4)
        process_list.setHorizontalHeaderLabels(["Заголовок", "Позиция (X, Y)", "Размер (ШxВ)", "PID"])
        process_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        process_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        process_list.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(process_list)
        
        # Нижняя часть - выбор пресета
        preset_label = QLabel("📋 Выберите пресет:")
        layout.addWidget(preset_label)
        
        preset_list_widget = QTableWidget()
        preset_list_widget.setColumnCount(3)
        preset_list_widget.setHorizontalHeaderLabels(["Имя", "Процесс", "Описание"])
        preset_list_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        preset_list_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        preset_list_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(preset_list_widget)
        
        # Загружаем процессы
        def load_processes(search_text=""):
            process_list.setRowCount(0)
            windows = self.normalizer.search_windows(search_text)
            for window in windows:
                row = process_list.rowCount()
                process_list.insertRow(row)
                process_list.setItem(row, 0, QTableWidgetItem(window.title))
                process_list.setItem(row, 1, QTableWidgetItem(f"{window.x}, {window.y}"))
                process_list.setItem(row, 2, QTableWidgetItem(f"{window.width} x {window.height}"))
                process_list.setItem(row, 3, QTableWidgetItem(str(window.pid or "N/A")))
        
        # Загружаем пресеты
        def load_presets(search_text=""):
            preset_list_widget.setRowCount(0)
            all_presets = self.storage.search_presets(search_text)
            for preset in all_presets:
                row = preset_list_widget.rowCount()
                preset_list_widget.insertRow(row)
                preset_list_widget.setItem(row, 0, QTableWidgetItem(preset.name))
                preset_list_widget.setItem(row, 1, QTableWidgetItem(preset.process_name))
                preset_list_widget.setItem(row, 2, QTableWidgetItem(preset.description))
        
        load_processes()
        load_presets()
        
        process_search.textChanged.connect(load_processes)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        apply_btn = QPushButton("✓ Применить")
        apply_btn.clicked.connect(lambda: self._on_process_and_preset_selected(
            dialog, process_list, preset_list_widget))
        buttons_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec()
    
    def _on_process_and_preset_selected(self, dialog: QDialog, 
                                         process_list: QTableWidget, 
                                         preset_list_widget: QTableWidget):
        """Обработчик выбора процесса и пресета."""
        process_selected = process_list.selectedItems()
        preset_selected = preset_list_widget.selectedItems()
        
        if not process_selected:
            QMessageBox.warning(self, "Предупреждение", "Выберите процесс!")
            return
        
        if not preset_selected:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        # Получаем данные выбранного процесса
        process_row = process_selected[0].row()
        process_title = process_list.item(process_row, 0).text()
        
        # Находим окно в списке по заголовку
        target_window = None
        for row in range(self.windows_table.rowCount()):
            title = self.windows_table.item(row, 0).text()
            if title == process_title:
                # Выбираем это окно в таблице
                self.windows_table.selectRow(row)
                target_window = self.current_window
                break
        
        if not target_window:
            QMessageBox.warning(self, "Предупреждение", 
                f"Окно '{process_title}' больше не доступно!")
            return
        
        # Применяем пресет к полям
        preset_row = preset_selected[0].row()
        all_presets = self.storage.get_all_presets()
        
        # Находим соответствующий пресет (по индексу в отфильтрованном списке)
        visible_presets = []
        search_text = ""  # Можно добавить поиск
        for preset in all_presets:
            if not search_text or search_text.lower() in preset.name.lower() or \
               search_text.lower() in preset.process_name.lower() or \
               search_text.lower() in preset.description.lower():
                visible_presets.append(preset)
        
        if preset_row < len(visible_presets):
            preset = visible_presets[preset_row]
            self._apply_preset_values(preset, apply_immediately=True)
            dialog.accept()
    
    def _delete_preset_dialog(self):
        """Показывает диалог выбора пресета для удаления."""
        dialog = QDialog(self)
        dialog.setWindowTitle("🗑️ Удалить пресет")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(300)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Выберите пресет для удаления:")
        layout.addWidget(label)
        
        # Таблица пресетов
        preset_list = QTableWidget()
        preset_list.setColumnCount(3)
        preset_list.setHorizontalHeaderLabels(["Имя", "Процесс", "Описание"])
        preset_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        preset_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        preset_list.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        all_presets = self.storage.get_all_presets()
        for preset in all_presets:
            row = preset_list.rowCount()
            preset_list.insertRow(row)
            preset_list.setItem(row, 0, QTableWidgetItem(preset.name))
            preset_list.setItem(row, 1, QTableWidgetItem(preset.process_name))
            preset_list.setItem(row, 2, QTableWidgetItem(preset.description))
        
        layout.addWidget(preset_list)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.clicked.connect(lambda: self._confirm_delete_preset(dialog, preset_list, all_presets))
        buttons_layout.addWidget(delete_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec()
    
    def _confirm_delete_preset(self, dialog: QDialog, preset_list: QTableWidget, presets: list[NormalizationPreset]):
        """Подтверждает и удаляет выбранный пресет."""
        selected_rows = preset_list.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет для удаления!")
            return
        
        row = selected_rows[0].row()
        preset = presets[row]
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить пресет '{preset.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.remove_preset(preset.id)
            QMessageBox.information(self, "Успех", f"Пресет '{preset.name}' удален!")
            dialog.accept()


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
        
        # Используем capture_with_preset для сохранения по пути из пресета
        self.preset_storage.capture_with_preset(
            preset=preset,
            screenshot_manager=self.screenshot_manager,
        )
        QMessageBox.information(self, "Успех", f"Скриншот сохранен в: {preset.screenshot_path}")
    
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
        
        # Создаем скриншот с использованием пресета (сохранение по пути из пресета)
        screenshot_preset = self.preset_storage.get_preset(screenshot_preset_id)
        if not screenshot_preset:
            QMessageBox.critical(self, "Ошибка", "Пресет скриншота не найден!")
            return
        
        self.preset_storage.capture_with_preset(
            preset=screenshot_preset,
            screenshot_manager=self.screenshot_manager,
        )
        
        QMessageBox.information(self, "Успех", f"Полный захват выполнен! Скриншот сохранен в: {screenshot_preset.screenshot_path}")


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
        name = self.name_input.text().strip()
        if not name:
            raise ValueError("Имя пресета не может быть пустым")
        
        screenshot_path = self.path_input.text().strip()
        # Если путь не указан, генерируем его на основе имени пресета
        if not screenshot_path:
            screenshot_path = f"presets/screenshots/{name}.png"
        # Убедимся, что путь имеет расширение .png
        elif not screenshot_path.endswith('.png'):
            screenshot_path = f"{screenshot_path}.png"
        
        return {
            "name": name,
            "process_preset_id": self.process_combo.currentData() or "default",
            "x": self.x_input.value(),
            "y": self.y_input.value(),
            "width": self.width_input.value(),
            "height": self.height_input.value(),
            "screenshot_path": screenshot_path,
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
        self.window_selection = WindowSelectionWidget(
            self.normalizer, self.preset_storage
        )
        self.content_stack.addWidget(self.window_selection)
        
        # Вкладка 2: Скриншоты
        self.screenshots = ScreenshotsWidget(self.screenshot_manager)
        self.content_stack.addWidget(self.screenshots)
        
        # Вкладка 3: Пресеты скриншотов
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
        self.btn_screenshots.clicked.connect(lambda: self._switch_tab(1))
        self.btn_screenshot_presets.clicked.connect(lambda: self._switch_tab(2))
    
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
