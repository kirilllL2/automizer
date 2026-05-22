"""
Главное окно приложения Automizer.
Современный красивый резиновый интерфейс с 3 вкладками:
1. Выбор процесса - выбор окна и настройка позиции/размеров
2. Пресеты скриншотов - управление пресетами скриншотов (скриншот создается автоматически)
3. CV распознавание - поиск областей на экране по изображениям пресетов
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QScrollArea, QGridLayout, QSpacerItem,
    QSizePolicy, QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QFormLayout, QSpinBox, QComboBox, QGraphicsDropShadowEffect, QCheckBox,
    QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, pyqtProperty, QVariantAnimation, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QAction, QCursor
from pathlib import Path

from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.window_manager import WindowManager, WindowInfo
from src.storage import PresetStorage
from src.screenshot import ScreenshotManager
from src.screenshot.presets import ScreenshotPresetStorage, ScreenshotPreset
from src.cv import CVMatcher, MatchResult
from src.macros.storage import MacroStorage, Macro
from src.macros.executor import MacroExecutor
from src.macros import (
    ActionType, ClickAbsoluteAction, ClickRelativeAction, ClickImageAction,
    DelayAction, ConditionAction, LoopAction, GotoAction, StateCheckAction,
    NormalizeWindowAction, FocusWindowAction, TakeScreenshotAction,
    ClickOffset, ConditionBranch
)
import uuid


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
        self.width_input.setRange(1, 10000)
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 10000)
        
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
        self.width_input.setRange(1, 10000)
        form.addRow("Ширина:", self.width_input)
        
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 10000)
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


class ScreenshotPresetsWidget(QWidget):
    """Виджет управления пресетами скриншотов (вкладка с автоскриншотами)."""
    
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
        title = QLabel("🎬 Пресеты скриншотов")
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
        self.presets_table.cellDoubleClicked.connect(self._open_screenshot_folder)
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
        
        self.refresh_btn = QPushButton("🔄 Обновить скриншот")
        self.refresh_btn.setObjectName("successBtn")
        self.refresh_btn.clicked.connect(self._refresh_screenshot)
        buttons_layout.addWidget(self.refresh_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Загружаем пресеты
        self._load_presets()
    
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
            self, "Добавление пресета скриншота", self.process_storage,
            screenshot_manager=self.screenshot_manager
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                # Проверяем: если пресет привязан к процессу, нормализуем его сначала
                if data["process_preset_id"]:
                    process_preset = self.process_storage.get_preset(data["process_preset_id"])
                    if process_preset:
                        # Нормализуем окно процесса перед созданием скриншота
                        self.normalizer.apply_preset(process_preset)
                
                self.preset_storage.add_preset(
                    **data,
                    screenshot_manager=self.screenshot_manager,
                    window_manager=self.normalizer.window_manager,
                )
                self._load_presets()
                QMessageBox.information(self, "Успех", "Пресет добавлен и скриншот создан!")
            except ValueError as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def _edit_preset(self):
        """Редактирует пресет."""
        preset = self._get_selected_preset()
        if not preset:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        dialog = ScreenshotPresetDialog(
            self, "Редактирование пресета скриншота", self.process_storage, preset,
            screenshot_manager=self.screenshot_manager
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            # Удаляем preset_id из data, т.к. он передается отдельно
            data.pop("preset_id", None)
            self.preset_storage.update_preset(preset_id=preset.id, **data)
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
            self.preset_storage.remove_preset(preset.id)
            self._load_presets()
    
    def _refresh_screenshot(self):
        """Обновляет скриншот для выбранного пресета."""
        preset = self._get_selected_preset()
        if not preset:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        # Если пресет привязан к процессу, сначала нормализуем его
        if preset.process_preset_id:
            process_preset = self.process_storage.get_preset(preset.process_preset_id)
            if process_preset:
                success = self.normalizer.apply_preset(process_preset)
                if not success:
                    QMessageBox.critical(self, "Ошибка", "Не удалось применить пресет процесса!")
                    return
            else:
                QMessageBox.critical(self, "Ошибка", "Пресет процесса не найден!")
                return
        
        # Для относительных координат обновляем window_id из текущего окна
        if preset.use_relative_coords:
            windows = self.normalizer.window_manager.get_windows()
            process_name = ""
            if preset.process_preset_id:
                process_preset = self.process_storage.get_preset(preset.process_preset_id)
                if process_preset:
                    process_name = process_preset.process_name
            
            for win in windows:
                if not process_name or process_name.lower() in win.title.lower():
                    preset.window_id = win.window_id
                    break
        
        # Создаем скриншот с использованием пресета
        self.preset_storage.capture_with_preset(
            preset=preset,
            screenshot_manager=self.screenshot_manager,
            window_manager=self.normalizer.window_manager if preset.use_relative_coords else None,
        )
        
        QMessageBox.information(self, "Успех", f"Скриншот обновлен! Сохранен в: {preset.screenshot_path}")
    
    def _open_screenshot_folder(self, row: int, column: int):
        """Открывает папку со скриншотом при двойном клике."""
        preset = self._get_selected_preset()
        if not preset:
            return
        
        import subprocess
        import sys
        import os
        
        # Получаем директорию файла скриншота
        screenshot_path = preset.screenshot_path
        if not screenshot_path:
            QMessageBox.warning(self, "Предупреждение", "Путь к скриншоту не указан!")
            return
        
        path = os.path.dirname(screenshot_path)
        # Преобразуем в абсолютный путь
        path = os.path.abspath(path)
        if not os.path.exists(path):
            QMessageBox.warning(self, "Предупреждение", f"Папка не найдена: {path}")
            return
        
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])


class ScreenshotPresetDialog(QDialog):
    """Диалог для создания/редактирования пресета скриншота."""
    
    def __init__(self, parent=None, title: str = "", 
                 process_storage: PresetStorage | None = None,
                 preset: ScreenshotPreset | None = None,
                 screenshot_manager=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.process_storage = process_storage
        self.preset = preset
        self.screenshot_manager = screenshot_manager
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
        self.process_combo.currentIndexChanged.connect(self._on_process_selected)
        form.addRow("Пресет процесса:", self.process_combo)
        
        # Переключатель типа координат
        self.relative_coords_checkbox = QCheckBox("Использовать относительные координаты окна")
        self.relative_coords_checkbox.setToolTip(
            "Если отмечено, координаты будут относительными для окна процесса.\n"
            "Скриншот можно делать даже если окно не активно или за другими окнами."
        )
        self.relative_coords_checkbox.stateChanged.connect(self._on_coord_type_changed)
        # Изначально отключаем чекбокс, пока не выбран пресет процесса
        self.relative_coords_checkbox.setEnabled(False)
        form.addRow("", self.relative_coords_checkbox)
        
        self.x_input = QSpinBox()
        self.x_input.setRange(-10000, 10000)
        form.addRow("X:", self.x_input)
        
        self.y_input = QSpinBox()
        self.y_input.setRange(-10000, 10000)
        form.addRow("Y:", self.y_input)
        
        self.width_input = QSpinBox()
        self.width_input.setRange(1, 10000)
        form.addRow("Ширина:", self.width_input)
        
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 10000)
        form.addRow("Высота:", self.height_input)
        
        # Кнопка предпросмотра области
        self.preview_btn = QPushButton("👁️ Показать область скриншота")
        self.preview_btn.setObjectName("secondaryBtn")
        self.preview_btn.clicked.connect(self._preview_screenshot_area)
        self.preview_btn.setToolTip("Показать область, которая будет захвачена")
        form.addRow("", self.preview_btn)
        
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
    
    def _on_coord_type_changed(self, state):
        """Обработчик изменения типа координат."""
        is_relative = self.relative_coords_checkbox.isChecked()
        process_preset_id = self.process_combo.currentData()
        
        # Если пресет процесса не выбран, принудительно устанавливаем глобальные координаты
        if not process_preset_id:
            self.relative_coords_checkbox.setChecked(False)
            self.relative_coords_checkbox.setEnabled(False)
            QMessageBox.information(
                self, "Информация",
                "Относительные координаты доступны только при выборе пресета процесса.\n"
                "Без пресета процесса будут использоваться глобальные координаты экрана."
            )
            self.x_input.setToolTip("Глобальная координата X на экране")
            self.y_input.setToolTip("Глобальная координата Y на экране")
        else:
            self.relative_coords_checkbox.setEnabled(True)
            if is_relative:
                self.x_input.setToolTip("Относительная координата X внутри окна (0 = левый край окна)")
                self.y_input.setToolTip("Относительная координата Y внутри окна (0 = верхний край окна)")
            else:
                self.x_input.setToolTip("Глобальная координата X на экране")
                self.y_input.setToolTip("Глобальная координата Y на экране")
    
    def _on_process_selected(self, index):
        """Обработчик выбора пресета процесса."""
        process_preset_id = self.process_combo.currentData()
        
        # Автоматически включаем относительные координаты если выбран пресет процесса
        if process_preset_id:
            self.relative_coords_checkbox.setChecked(True)
            self.relative_coords_checkbox.setEnabled(True)
            self.x_input.setToolTip("Относительная координата X внутри окна (0 = левый край окна)")
            self.y_input.setToolTip("Относительная координата Y внутри окна (0 = верхний край окна)")
        else:
            self.relative_coords_checkbox.setChecked(False)
            self.relative_coords_checkbox.setEnabled(False)
            self.x_input.setToolTip("Глобальная координата X на экране")
            self.y_input.setToolTip("Глобальная координата Y на экране")
    
    def _preview_screenshot_area(self):
        """Показывает область скриншота."""
        x = self.x_input.value()
        y = self.y_input.value()
        width = self.width_input.value()
        height = self.height_input.value()
        is_relative = self.relative_coords_checkbox.isChecked()
        
        if is_relative:
            # Для относительных координат нужно найти окно процесса
            process_preset_id = self.process_combo.currentData()
            if not process_preset_id:
                QMessageBox.warning(
                    self, "Предупреждение",
                    "Для предпросмотра относительных координат выберите пресет процесса!"
                )
                return
            
            # Получаем пресет процесса и находим окно
            from src.normalizer import ProcessNormalizer
            from src.window_manager import WindowManager
            
            window_manager = WindowManager()
            normalizer = ProcessNormalizer(window_manager)
            
            # Ищем окно по имени процесса из пресета
            process_preset = self.process_storage.get_preset(process_preset_id)
            if not process_preset:
                QMessageBox.warning(self, "Ошибка", "Пресет процесса не найден!")
                return
            
            # Находим окно по имени процесса
            windows = window_manager.get_windows()
            target_window = None
            for window in windows:
                if process_preset.process_name.lower() in window.title.lower():
                    target_window = window
                    break
            
            if not target_window:
                QMessageBox.warning(
                    self, "Предупреждение",
                    f"Окно процесса '{process_preset.process_name}' не найдено!\n"
                    "Запустите приложение для предпросмотра."
                )
                return
            
            # Конвертируем относительные координаты в глобальные
            global_x = target_window.x + x
            global_y = target_window.y + y
            
            # Показываем превью с глобальными координатами
            if self.screenshot_manager:
                self.screenshot_manager.preview_area(
                    global_x, global_y, width, height
                )
        else:
            # Для глобальных координат показываем напрямую
            if self.screenshot_manager:
                self.screenshot_manager.preview_area(x, y, width, height)
    
    def _fill_data(self, preset: ScreenshotPreset):
        """Заполняет форму данными пресета."""
        self.name_input.setText(preset.name)
        
        # Устанавливаем пресет процесса по ID
        process_preset_id = preset.process_preset_id
        index = self.process_combo.findData(process_preset_id)
        if index >= 0:
            self.process_combo.setCurrentIndex(index)
        else:
            # Если пресет процесса не найден, оставляем пустым
            self.process_combo.setCurrentIndex(0)
        
        self.x_input.setValue(preset.x)
        self.y_input.setValue(preset.y)
        self.width_input.setValue(preset.width)
        self.height_input.setValue(preset.height)
        self.path_input.setText(preset.screenshot_path)
        self.desc_input.setText(preset.description)
        # Устанавливаем состояние чекбокса относительных координат
        # Важно: сначала устанавливаем значение, чтобы триггернуть обновление tooltip
        self.relative_coords_checkbox.blockSignals(True)
        self.relative_coords_checkbox.setChecked(preset.use_relative_coords)
        self.relative_coords_checkbox.blockSignals(False)
        # Обновляем enabled state и tooltip в соответствии с наличием process_preset_id
        has_process_preset = self.process_combo.currentData() != ""
        self.relative_coords_checkbox.setEnabled(has_process_preset)
        self._on_coord_type_changed(0)  # Обновляем tooltip
    
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
        
        process_preset_id = self.process_combo.currentData()
        use_relative_coords = self.relative_coords_checkbox.isChecked()
        
        # Если пресет процесса не выбран, используем глобальные координаты
        if not process_preset_id:
            use_relative_coords = False
        
        # Генерируем preset_id из имени (для нового пресета) или используем существующий
        preset_id = self.preset.id if self.preset else name.lower().replace(" ", "_")
        
        # Получаем window_id если используются относительные координаты
        window_id = None
        if use_relative_coords and process_preset_id and self.process_storage:
            process_preset = self.process_storage.get_preset(process_preset_id)
            if process_preset:
                # Ищем окно по имени процесса из пресета нормализации (используем WindowManager)
                from src.window_manager import WindowManager
                window_manager = WindowManager()
                windows = window_manager.get_windows()
                for window in windows:
                    if process_preset.process_name.lower() in window.title.lower():
                        window_id = window.window_id
                        break
        
        return {
            "preset_id": preset_id,
            "name": name,
            "process_preset_id": process_preset_id or "default",
            "x": self.x_input.value(),
            "y": self.y_input.value(),
            "width": self.width_input.value(),
            "height": self.height_input.value(),
            "screenshot_path": screenshot_path,
            "description": self.desc_input.text(),
            "use_relative_coords": use_relative_coords,
            "window_id": window_id,
        }


class MacrosWidget(QWidget):
    """Виджет для управления макросами - создание, редактирование, запуск."""
    
    def __init__(self, 
                 macro_storage: MacroStorage,
                 macro_executor: MacroExecutor,
                 screenshot_preset_storage: ScreenshotPresetStorage,
                 preset_storage: PresetStorage):
        super().__init__()
        self.macro_storage = macro_storage
        self.macro_executor = macro_executor
        self.screenshot_preset_storage = screenshot_preset_storage
        self.preset_storage = preset_storage
        self.current_macro: Macro | None = None
        self._setup_ui()
        self._connect_executor_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING)
        layout.setContentsMargins(ModernStyle.PADDING, ModernStyle.PADDING,
                                   ModernStyle.PADDING, ModernStyle.PADDING)
        
        # Заголовок
        title = QLabel("🎬 Макросы")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Верхняя панель со списком макросов и кнопками
        top_layout = QHBoxLayout()
        
        # Список макросов
        macros_list_card = QFrame()
        macros_list_card.setObjectName("card")
        macros_list_layout = QVBoxLayout(macros_list_card)
        
        list_header = QHBoxLayout()
        list_title = QLabel("📋 Список макросов")
        list_title.setObjectName("sectionTitle")
        list_header.addWidget(list_title)
        list_header.addStretch()
        
        self.new_macro_btn = QPushButton("➕ Новый")
        self.new_macro_btn.clicked.connect(self._create_new_macro)
        list_header.addWidget(self.new_macro_btn)
        
        macros_list_layout.addLayout(list_header)
        
        self.macros_table = QTableWidget()
        self.macros_table.setColumnCount(3)
        self.macros_table.setHorizontalHeaderLabels(["Название", "Описание", "Действий"])
        self.macros_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.macros_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.macros_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.macros_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.macros_table.itemSelectionChanged.connect(self._on_macro_selected)
        macros_list_layout.addWidget(self.macros_table)
        
        top_layout.addWidget(macros_list_card, stretch=1)
        
        # Панель редактора
        editor_card = QFrame()
        editor_card.setObjectName("card")
        editor_layout = QVBoxLayout(editor_card)
        
        editor_title = QLabel("✏️ Редактор макроса")
        editor_title.setObjectName("sectionTitle")
        editor_layout.addWidget(editor_title)
        
        # Информация о макросе
        info_layout = QGridLayout()
        info_layout.setSpacing(8)
        
        info_layout.addWidget(QLabel("Название:"), 0, 0)
        self.macro_name_input = QLineEdit()
        self.macro_name_input.setPlaceholderText("Название макроса")
        info_layout.addWidget(self.macro_name_input, 0, 1)
        
        info_layout.addWidget(QLabel("Описание:"), 0, 2)
        self.macro_desc_input = QLineEdit()
        self.macro_desc_input.setPlaceholderText("Описание макроса")
        info_layout.addWidget(self.macro_desc_input, 0, 3)
        
        editor_layout.addLayout(info_layout)
        
        # Список действий
        actions_title = QLabel("📝 Действия макроса")
        actions_title.setObjectName("sectionTitle")
        editor_layout.addWidget(actions_title)
        
        self.actions_table = QTableWidget()
        self.actions_table.setColumnCount(5)
        self.actions_table.setHorizontalHeaderLabels(["#", "Тип", "Метка (Label)", "Описание", "Включено"])
        self.actions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.actions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.actions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.actions_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.actions_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.actions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.actions_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.actions_table.itemSelectionChanged.connect(self._on_action_selected)
        self.actions_table.cellDoubleClicked.connect(self._edit_action)
        editor_layout.addWidget(self.actions_table)
        
        # Кнопки управления действиями
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(8)
        
        self.add_action_btn = QPushButton("➕ Добавить действие")
        self.add_action_btn.clicked.connect(self._add_action)
        self.add_action_btn.setEnabled(False)
        action_buttons_layout.addWidget(self.add_action_btn)
        
        self.edit_action_btn = QPushButton("✏️ Редактировать")
        self.edit_action_btn.clicked.connect(self._edit_action)
        self.edit_action_btn.setEnabled(False)
        action_buttons_layout.addWidget(self.edit_action_btn)
        
        self.remove_action_btn = QPushButton("🗑️ Удалить")
        self.remove_action_btn.setObjectName("dangerBtn")
        self.remove_action_btn.clicked.connect(self._remove_action)
        self.remove_action_btn.setEnabled(False)
        action_buttons_layout.addWidget(self.remove_action_btn)
        
        self.move_up_btn = QPushButton("⬆️ Вверх")
        self.move_up_btn.clicked.connect(self._move_action_up)
        self.move_up_btn.setEnabled(False)
        action_buttons_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("⬇️ Вниз")
        self.move_down_btn.clicked.connect(self._move_action_down)
        self.move_down_btn.setEnabled(False)
        action_buttons_layout.addWidget(self.move_down_btn)
        
        action_buttons_layout.addStretch()
        editor_layout.addLayout(action_buttons_layout)
        
        # Кнопки управления макросом
        macro_buttons_layout = QHBoxLayout()
        macro_buttons_layout.setSpacing(8)
        
        self.save_macro_btn = QPushButton("💾 Сохранить")
        self.save_macro_btn.setObjectName("successBtn")
        self.save_macro_btn.clicked.connect(self._save_macro)
        self.save_macro_btn.setEnabled(False)
        macro_buttons_layout.addWidget(self.save_macro_btn)
        
        self.run_macro_btn = QPushButton("▶️ Запустить")
        self.run_macro_btn.clicked.connect(self._run_macro)
        self.run_macro_btn.setEnabled(False)
        macro_buttons_layout.addWidget(self.run_macro_btn)
        
        self.stop_macro_btn = QPushButton("⏹️ Остановить")
        self.stop_macro_btn.setObjectName("dangerBtn")
        self.stop_macro_btn.clicked.connect(self._stop_macro)
        self.stop_macro_btn.setEnabled(False)
        macro_buttons_layout.addWidget(self.stop_macro_btn)
        
        macro_buttons_layout.addStretch()
        editor_layout.addLayout(macro_buttons_layout)
        
        # Статус выполнения
        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QVBoxLayout(status_card)
        
        status_title = QLabel("📊 Статус выполнения")
        status_title.setObjectName("sectionTitle")
        status_layout.addWidget(status_title)
        
        self.status_label = QLabel("Готов к работе")
        self.status_label.setStyleSheet(f"font-size: 16px; color: {ModernStyle.TEXT_PRIMARY};")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {ModernStyle.BG_PRIMARY};
                border: 2px solid {ModernStyle.BORDER};
                border-radius: 6px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {ModernStyle.ACCENT};
                border-radius: 6px;
            }}
        """)
        status_layout.addWidget(self.progress_bar)
        
        editor_layout.addWidget(status_card)
        
        top_layout.addWidget(editor_card, stretch=2)
        
        layout.addLayout(top_layout)
        
        # Загружаем список макросов
        self._load_macros_list()
    
    def _connect_executor_signals(self):
        """Подключает сигналы исполнителя макросов."""
        self.macro_executor.on_action_start = self._on_action_start
        self.macro_executor.on_action_complete = self._on_action_complete
        self.macro_executor.on_action_error = self._on_action_error
        self.macro_executor.on_macro_complete = self._on_macro_complete
        self.macro_executor.on_macro_error = self._on_macro_error
    
    def _load_macros_list(self):
        """Загружает список макросов в таблицу."""
        self.macros_table.setRowCount(0)
        macros = self.macro_storage.get_all_macros()
        
        for macro in macros:
            row = self.macros_table.rowCount()
            self.macros_table.insertRow(row)
            self.macros_table.setItem(row, 0, QTableWidgetItem(macro.name))
            self.macros_table.setItem(row, 1, QTableWidgetItem(macro.description or "-"))
            self.macros_table.setItem(row, 2, QTableWidgetItem(str(len(macro.actions))))
    
    def _on_macro_selected(self):
        """Обработчик выбора макроса в списке."""
        selected_rows = self.macros_table.selectedItems()
        if not selected_rows:
            self.current_macro = None
            self._clear_editor()
            return
        
        row = selected_rows[0].row()
        macro_id = self.macros_table.item(row, 0).text()
        
        # Находим макрос по имени (в реальном приложении лучше использовать ID)
        macros = self.macro_storage.get_all_macros()
        for macro in macros:
            if macro.name == macro_id:
                self.current_macro = macro
                break
        
        if self.current_macro:
            self._load_macro_into_editor()
    
    def _clear_editor(self):
        """Очищает редактор."""
        self.macro_name_input.clear()
        self.macro_desc_input.clear()
        self.actions_table.setRowCount(0)
        self.add_action_btn.setEnabled(False)
        self.edit_action_btn.setEnabled(False)
        self.remove_action_btn.setEnabled(False)
        self.move_up_btn.setEnabled(False)
        self.move_down_btn.setEnabled(False)
        self.save_macro_btn.setEnabled(False)
        self.run_macro_btn.setEnabled(False)
    
    def _load_macro_into_editor(self):
        """Загружает макрос в редактор."""
        if not self.current_macro:
            return
        
        self.macro_name_input.setText(self.current_macro.name)
        self.macro_desc_input.setText(self.current_macro.description or "")
        
        self.actions_table.setRowCount(0)
        for i, action in enumerate(self.current_macro.actions):
            row = self.actions_table.rowCount()
            self.actions_table.insertRow(row)
            
            type_name = action.type.value.replace("_", " ").title()
            self.actions_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
            self.actions_table.setItem(row, 1, QTableWidgetItem(type_name))
            self.actions_table.setItem(row, 2, QTableWidgetItem(action.label or "-"))
            self.actions_table.setItem(row, 3, QTableWidgetItem(action.description or "-"))
            
            enabled_item = QTableWidgetItem("✓" if action.enabled else "✗")
            enabled_item.setFlags(enabled_item.flags() & ~Qt.ItemIsEditable)
            self.actions_table.setItem(row, 4, enabled_item)
        
        self.add_action_btn.setEnabled(True)
        self.save_macro_btn.setEnabled(True)
        self.run_macro_btn.setEnabled(True)
    
    def _create_new_macro(self):
        """Создает новый макрос."""
        dialog = NewMacroDialog(self)
        if dialog.exec():
            name, description = dialog.get_data()
            macro_id = str(uuid.uuid4())[:8]
            
            try:
                macro = self.macro_storage.create_macro(macro_id, name, description)
                self.current_macro = macro
                self._load_macros_list()
                self._load_macro_into_editor()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать макрос: {e}")
    
    def _add_action(self):
        """Добавляет новое действие."""
        if not self.current_macro:
            return
        
        dialog = ActionDialog(self, preset_storage=self.preset_storage, screenshot_preset_storage=self.screenshot_preset_storage)
        if dialog.exec():
            action = dialog.get_action()
            if action:
                self.current_macro.add_action(action)
                self._load_macro_into_editor()
    
    def _edit_action(self):
        """Редактирует выбранное действие."""
        if not self.current_macro:
            return
        
        selected_rows = self.actions_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        action = self.current_macro.actions[row]
        
        dialog = ActionDialog(self, action=action, preset_storage=self.preset_storage, screenshot_preset_storage=self.screenshot_preset_storage)
        if dialog.exec():
            new_action = dialog.get_action()
            if new_action:
                self.current_macro.actions[row] = new_action
                self._load_macro_into_editor()
    
    def _remove_action(self):
        """Удаляет выбранное действие."""
        if not self.current_macro:
            return
        
        selected_rows = self.actions_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Удалить это действие?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_macro.remove_action(self.current_macro.actions[row].id)
            self._load_macro_into_editor()
    
    def _move_action_up(self):
        """Перемещает действие вверх."""
        if not self.current_macro:
            return
        
        selected_rows = self.actions_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row > 0:
            actions = self.current_macro.actions
            actions[row], actions[row - 1] = actions[row - 1], actions[row]
            self._load_macro_into_editor()
            self.actions_table.selectRow(row - 1)
    
    def _move_action_down(self):
        """Перемещает действие вниз."""
        if not self.current_macro:
            return
        
        selected_rows = self.actions_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row < len(self.current_macro.actions) - 1:
            actions = self.current_macro.actions
            actions[row], actions[row + 1] = actions[row + 1], actions[row]
            self._load_macro_into_editor()
            self.actions_table.selectRow(row + 1)
    
    def _on_action_selected(self):
        """Обработчик выбора действия."""
        selected = bool(self.actions_table.selectedItems())
        self.edit_action_btn.setEnabled(selected)
        self.remove_action_btn.setEnabled(selected)
        self.move_up_btn.setEnabled(selected)
        self.move_down_btn.setEnabled(selected)
    
    def _save_macro(self):
        """Сохраняет макрос."""
        if not self.current_macro:
            return
        
        self.current_macro.name = self.macro_name_input.text()
        self.current_macro.description = self.macro_desc_input.text()
        
        try:
            self.macro_storage.update_macro(self.current_macro)
            self._load_macros_list()
            QMessageBox.information(self, "Успешно", "Макрос сохранен!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить макрос: {e}")
    
    def _run_macro(self):
        """Запускает макрос."""
        if not self.current_macro:
            return
        
        # Сохраняем перед запуском
        self._save_macro()
        
        self.status_label.setText("Выполнение...")
        self.status_label.setStyleSheet(f"font-size: 16px; color: {ModernStyle.SUCCESS};")
        self.run_macro_btn.setEnabled(False)
        self.stop_macro_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # Запускаем в отдельном потоке (упрощенно - синхронно)
        try:
            self.macro_executor.execute(self.current_macro)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка выполнения", str(e))
            self._reset_status()
    
    def _stop_macro(self):
        """Останавливает выполнение макроса."""
        self.macro_executor.stop()
        self._reset_status()
    
    def _reset_status(self):
        """Сбрасывает статус."""
        self.status_label.setText("Готов к работе")
        self.status_label.setStyleSheet(f"font-size: 16px; color: {ModernStyle.TEXT_PRIMARY};")
        self.run_macro_btn.setEnabled(True)
        self.stop_macro_btn.setEnabled(False)
        self.progress_bar.setValue(0)
    
    def _on_action_start(self, action, index):
        """Вызывается при начале выполнения действия."""
        self.status_label.setText(f"Действие {index + 1}: {action.type.value}")
        total = len(self.current_macro.actions) if self.current_macro else 1
        progress = int((index / total) * 100)
        self.progress_bar.setValue(progress)
    
    def _on_action_complete(self, action, index):
        """Вызывается при завершении действия."""
        pass
    
    def _on_action_error(self, action, index, error):
        """Вызывается при ошибке выполнения действия."""
        self.status_label.setText(f"Ошибка: {error}")
        self.status_label.setStyleSheet(f"font-size: 16px; color: {ModernStyle.DANGER};")
    
    def _on_macro_complete(self, macro):
        """Вызывается при завершении макроса."""
        self.status_label.setText("Макрос выполнен успешно!")
        self.status_label.setStyleSheet(f"font-size: 16px; color: {ModernStyle.SUCCESS};")
        self.progress_bar.setValue(100)
        self._reset_status()
    
    def _on_macro_error(self, macro, error):
        """Вызывается при ошибке выполнения макроса."""
        self.status_label.setText(f"Ошибка макроса: {error}")
        self.status_label.setStyleSheet(f"font-size: 16px; color: {ModernStyle.DANGER};")
        self._reset_status()


class NewMacroDialog(QDialog):
    """Диалог создания нового макроса."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый макрос")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название макроса")
        form_layout.addRow("Название:", self.name_input)
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Описание макроса")
        form_layout.addRow("Описание:", self.desc_input)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_data(self) -> tuple[str, str]:
        return self.name_input.text(), self.desc_input.text()


class ActionDialog(QDialog):
    """Диалог создания/редактирования действия макроса."""
    
    def __init__(self, parent=None, action: Optional[Any] = None, 
                 preset_storage: PresetStorage = None,
                 screenshot_preset_storage: ScreenshotPresetStorage = None):
        super().__init__(parent)
        self.action = action
        self.preset_storage = preset_storage or PresetStorage()
        self.screenshot_preset_storage = screenshot_preset_storage or ScreenshotPresetStorage()
        
        self.setWindowTitle("Редактирование действия" if action else "Новое действие")
        self.setMinimumSize(600, 700)
        
        self._setup_ui()
        if action:
            self._load_action()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Тип действия
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип действия:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "click_absolute", "click_relative", "click_image",
            "delay", "condition", "loop", "goto", "state_check",
            "normalize_window", "focus_window", "take_screenshot"
        ])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Общие настройки
        common_group = QGroupBox("Общие настройки")
        common_layout = QFormLayout(common_group)
        
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Метка для переходов (Label)")
        common_layout.addRow("Метка (Label):", self.label_input)
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Описание действия")
        common_layout.addRow("Описание:", self.desc_input)
        
        self.enabled_check = QCheckBox("Включено")
        self.enabled_check.setChecked(True)
        common_layout.addRow("", self.enabled_check)
        
        retry_layout = QHBoxLayout()
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setRange(0, 10)
        self.retry_count_spin.setValue(0)
        retry_layout.addWidget(self.retry_count_spin)
        retry_layout.addWidget(QLabel("повторений"))
        common_layout.addRow("Повторы при ошибке:", retry_layout)
        
        retry_delay_layout = QHBoxLayout()
        self.retry_delay_spin = QDoubleSpinBox()
        self.retry_delay_spin.setRange(0.1, 60.0)
        self.retry_delay_spin.setValue(1.0)
        self.retry_delay_spin.setSingleStep(0.5)
        retry_delay_layout.addWidget(self.retry_delay_spin)
        retry_delay_layout.addWidget(QLabel("сек"))
        common_layout.addRow("Задержка между повторами:", retry_delay_layout)
        
        layout.addWidget(common_group)
        
        # Специфичные настройки для каждого типа
        self.settings_stack = QStackedWidget()
        
        # Click Absolute
        abs_widget = QWidget()
        abs_layout = QFormLayout(abs_widget)
        self.abs_x_spin = QSpinBox()
        self.abs_x_spin.setRange(-10000, 10000)
        abs_layout.addRow("X:", self.abs_x_spin)
        self.abs_y_spin = QSpinBox()
        self.abs_y_spin.setRange(-10000, 10000)
        abs_layout.addRow("Y:", self.abs_y_spin)
        self.abs_button_combo = QComboBox()
        self.abs_button_combo.addItems(["left", "right", "middle"])
        abs_layout.addRow("Кнопка:", self.abs_button_combo)
        self.abs_double_check = QCheckBox("Двойной клик")
        abs_layout.addRow("", self.abs_double_check)
        self._add_offset_settings(abs_layout)
        self.settings_stack.addWidget(abs_widget)
        
        # Click Relative
        rel_widget = QWidget()
        rel_layout = QFormLayout(rel_widget)
        self.rel_preset_combo = QComboBox()
        self._update_presets()
        rel_layout.addRow("Пресет окна:", self.rel_preset_combo)
        self.rel_x_spin = QSpinBox()
        self.rel_x_spin.setRange(-10000, 10000)
        rel_layout.addRow("X (относительно):", self.rel_x_spin)
        self.rel_y_spin = QSpinBox()
        self.rel_y_spin.setRange(-10000, 10000)
        rel_layout.addRow("Y (относительно):", self.rel_y_spin)
        self.rel_button_combo = QComboBox()
        self.rel_button_combo.addItems(["left", "right", "middle"])
        rel_layout.addRow("Кнопка:", self.rel_button_combo)
        self.rel_double_check = QCheckBox("Двойной клик")
        rel_layout.addRow("", self.rel_double_check)
        self._add_offset_settings(rel_layout)
        self.settings_stack.addWidget(rel_widget)
        
        # Click Image
        img_widget = QWidget()
        img_layout = QFormLayout(img_widget)
        self.img_preset_combo = QComboBox()
        self._update_screenshot_presets()
        img_layout.addRow("Пресет изображения:", self.img_preset_combo)
        self.img_confidence_spin = QDoubleSpinBox()
        self.img_confidence_spin.setRange(0.1, 1.0)
        self.img_confidence_spin.setSingleStep(0.05)
        self.img_confidence_spin.setValue(0.8)
        img_layout.addRow("Порог уверенности:", self.img_confidence_spin)
        self.img_position_combo = QComboBox()
        self.img_position_combo.addItems(["center", "top_left", "random"])
        img_layout.addRow("Позиция клика:", self.img_position_combo)
        self.img_button_combo = QComboBox()
        self.img_button_combo.addItems(["left", "right", "middle"])
        img_layout.addRow("Кнопка:", self.img_button_combo)
        self.img_double_check = QCheckBox("Двойной клик")
        img_layout.addRow("", self.img_double_check)
        self._add_offset_settings(img_layout)
        self.settings_stack.addWidget(img_widget)
        
        # Delay
        delay_widget = QWidget()
        delay_layout = QFormLayout(delay_widget)
        self.delay_duration_spin = QDoubleSpinBox()
        self.delay_duration_spin.setRange(0.1, 3600.0)
        self.delay_duration_spin.setSingleStep(0.5)
        self.delay_duration_spin.setValue(1.0)
        delay_layout.addRow("Длительность (сек):", self.delay_duration_spin)
        self.settings_stack.addWidget(delay_widget)
        
        # Condition
        cond_widget = QWidget()
        cond_layout = QFormLayout(cond_widget)
        self.cond_type_combo = QComboBox()
        self.cond_type_combo.addItems(["image_exists", "image_not_exists", "color_at_pixel"])
        self.cond_type_combo.currentTextChanged.connect(self._on_condition_type_changed)
        cond_layout.addRow("Тип условия:", self.cond_type_combo)
        
        self.cond_preset_combo = QComboBox()
        self._update_screenshot_presets()
        cond_layout.addRow("Пресет изображения:", self.cond_preset_combo)
        self.cond_confidence_spin = QDoubleSpinBox()
        self.cond_confidence_spin.setRange(0.1, 1.0)
        self.cond_confidence_spin.setSingleStep(0.05)
        self.cond_confidence_spin.setValue(0.8)
        cond_layout.addRow("Порог уверенности:", self.cond_confidence_spin)
        
        self.cond_color_layout = QHBoxLayout()
        self.cond_x_spin = QSpinBox()
        self.cond_x_spin.setRange(-10000, 10000)
        self.cond_color_layout.addWidget(self.cond_x_spin)
        self.cond_y_spin = QSpinBox()
        self.cond_y_spin.setRange(-10000, 10000)
        self.cond_color_layout.addWidget(self.cond_y_spin)
        cond_layout.addRow("Координаты для проверки цвета:", self.cond_color_layout)
        
        self.cond_true_goto = QLineEdit()
        cond_layout.addRow("Переход если True (Label):", self.cond_true_goto)
        self.cond_false_goto = QLineEdit()
        cond_layout.addRow("Переход если False (Label):", self.cond_false_goto)
        self.settings_stack.addWidget(cond_widget)
        
        # Loop
        loop_widget = QWidget()
        loop_layout = QFormLayout(loop_widget)
        self.loop_type_combo = QComboBox()
        self.loop_type_combo.addItems(["count", "while_image_exists", "while_image_not_exists"])
        self.loop_type_combo.currentTextChanged.connect(self._on_loop_type_changed)
        loop_layout.addRow("Тип цикла:", self.loop_type_combo)
        self.loop_iterations_spin = QSpinBox()
        self.loop_iterations_spin.setRange(1, 1000)
        self.loop_iterations_spin.setValue(1)
        loop_layout.addRow("Количество итераций:", self.loop_iterations_spin)
        self.loop_max_spin = QSpinBox()
        self.loop_max_spin.setRange(1, 10000)
        self.loop_max_spin.setValue(100)
        loop_layout.addRow("Макс. итераций:", self.loop_max_spin)
        self.settings_stack.addWidget(loop_widget)
        
        # Goto
        goto_widget = QWidget()
        goto_layout = QFormLayout(goto_widget)
        self.goto_target_input = QLineEdit()
        goto_layout.addRow("Целевая метка (Label):", self.goto_target_input)
        self.settings_stack.addWidget(goto_widget)
        
        # State Check
        state_widget = QWidget()
        state_layout = QFormLayout(state_widget)
        self.state_area_type_combo = QComboBox()
        self.state_area_type_combo.addItems(["absolute", "relative"])
        state_layout.addRow("Тип области:", self.state_area_type_combo)
        self.state_x_spin = QSpinBox()
        self.state_x_spin.setRange(-10000, 10000)
        self.state_x_spin.setValue(0)
        state_layout.addRow("X:", self.state_x_spin)
        self.state_y_spin = QSpinBox()
        self.state_y_spin.setRange(-10000, 10000)
        self.state_y_spin.setValue(0)
        state_layout.addRow("Y:", self.state_y_spin)
        self.state_w_spin = QSpinBox()
        self.state_w_spin.setRange(1, 10000)
        self.state_w_spin.setValue(100)
        state_layout.addRow("Ширина:", self.state_w_spin)
        self.state_h_spin = QSpinBox()
        self.state_h_spin.setRange(1, 10000)
        self.state_h_spin.setValue(100)
        state_layout.addRow("Высота:", self.state_h_spin)
        self.state_wait_spin = QDoubleSpinBox()
        self.state_wait_spin.setRange(0.1, 60.0)
        self.state_wait_spin.setSingleStep(0.5)
        self.state_wait_spin.setValue(1.0)
        state_layout.addRow("Время ожидания (сек):", self.state_wait_spin)
        self.state_threshold_spin = QDoubleSpinBox()
        self.state_threshold_spin.setRange(0.5, 1.0)
        self.state_threshold_spin.setSingleStep(0.05)
        self.state_threshold_spin.setValue(0.95)
        state_layout.addRow("Порог схожести:", self.state_threshold_spin)
        self.state_unchanged_spin = QSpinBox()
        self.state_unchanged_spin.setRange(1, 10)
        self.state_unchanged_spin.setValue(1)
        state_layout.addRow("Проверок для 'не изменилось':", self.state_unchanged_spin)
        self.state_changed_spin = QSpinBox()
        self.state_changed_spin.setRange(1, 10)
        self.state_changed_spin.setValue(1)
        state_layout.addRow("Проверок для 'изменилось':", self.state_changed_spin)
        self.state_unchanged_goto = QLineEdit()
        state_layout.addRow("Переход если не изменилось (Label):", self.state_unchanged_goto)
        self.state_changed_goto = QLineEdit()
        state_layout.addRow("Переход если изменилось (Label):", self.state_changed_goto)
        self.settings_stack.addWidget(state_widget)
        
        # Normalize Window
        norm_widget = QWidget()
        norm_layout = QFormLayout(norm_widget)
        self.norm_preset_combo = QComboBox()
        self._update_presets()
        norm_layout.addRow("Пресет нормализации:", self.norm_preset_combo)
        self.settings_stack.addWidget(norm_widget)
        
        # Focus Window
        focus_widget = QWidget()
        focus_layout = QFormLayout(focus_widget)
        self.focus_preset_combo = QComboBox()
        self._update_presets()
        focus_layout.addRow("Пресет окна:", self.focus_preset_combo)
        self.settings_stack.addWidget(focus_widget)
        
        # Take Screenshot
        shot_widget = QWidget()
        shot_layout = QFormLayout(shot_widget)
        self.shot_id_input = QLineEdit()
        shot_layout.addRow("ID скриншота:", self.shot_id_input)
        self.shot_x_spin = QSpinBox()
        self.shot_x_spin.setRange(-10000, 10000)
        shot_layout.addRow("X:", self.shot_x_spin)
        self.shot_y_spin = QSpinBox()
        self.shot_y_spin.setRange(-10000, 10000)
        shot_layout.addRow("Y:", self.shot_y_spin)
        self.shot_w_spin = QSpinBox()
        self.shot_w_spin.setRange(1, 10000)
        shot_layout.addRow("Ширина:", self.shot_w_spin)
        self.shot_h_spin = QSpinBox()
        self.shot_h_spin.setRange(1, 10000)
        shot_layout.addRow("Высота:", self.shot_h_spin)
        self.settings_stack.addWidget(shot_widget)
        
        layout.addWidget(self.settings_stack)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Устанавливаем первый тип
        self._on_type_changed(self.type_combo.currentText())
    
    def _add_offset_settings(self, layout: QFormLayout):
        """Добавляет настройки отклонения."""
        offset_group = QGroupBox("Отклонение координат")
        offset_layout = QFormLayout(offset_group)
        
        self.offset_enabled = QCheckBox("Включить случайное отклонение")
        self.offset_enabled.setChecked(True)
        offset_layout.addRow("", self.offset_enabled)
        
        offset_x_layout = QHBoxLayout()
        self.offset_x_spin = QSpinBox()
        self.offset_x_spin.setRange(0, 100)
        self.offset_x_spin.setValue(5)
        offset_x_layout.addWidget(self.offset_x_spin)
        offset_x_layout.addWidget(QLabel("px"))
        offset_layout.addRow("Макс. отклонение X:", offset_x_layout)
        
        offset_y_layout = QHBoxLayout()
        self.offset_y_spin = QSpinBox()
        self.offset_y_spin.setRange(0, 100)
        self.offset_y_spin.setValue(5)
        offset_y_layout.addWidget(self.offset_y_spin)
        offset_y_layout.addWidget(QLabel("px"))
        offset_layout.addRow("Макс. отклонение Y:", offset_y_layout)
        
        layout.addRow("", offset_group)
    
    def _update_presets(self):
        """Обновляет список пресетов нормализации."""
        self.rel_preset_combo.clear()
        self.norm_preset_combo.clear()
        self.focus_preset_combo.clear()
        
        presets = self.preset_storage.get_all_presets()
        for preset in presets:
            display = f"{preset.name} ({preset.process_name})"
            self.rel_preset_combo.addItem(display, preset.id)
            self.norm_preset_combo.addItem(display, preset.id)
            self.focus_preset_combo.addItem(display, preset.id)
    
    def _update_screenshot_presets(self):
        """Обновляет список пресетов скриншотов."""
        self.img_preset_combo.clear()
        self.cond_preset_combo.clear()
        
        presets = self.screenshot_preset_storage.get_all_presets()
        for preset in presets:
            self.img_preset_combo.addItem(preset.name, preset.id)
            self.cond_preset_combo.addItem(preset.name, preset.id)
    
    def _on_type_changed(self, type_name: str):
        """Переключает вид настроек в зависимости от типа."""
        type_map = {
            "click_absolute": 0,
            "click_relative": 1,
            "click_image": 2,
            "delay": 3,
            "condition": 4,
            "loop": 5,
            "goto": 6,
            "state_check": 7,
            "normalize_window": 8,
            "focus_window": 9,
            "take_screenshot": 10,
        }
        self.settings_stack.setCurrentIndex(type_map.get(type_name, 0))
    
    def _on_condition_type_changed(self, type_name: str):
        """Показывает/скрывает поля для проверки цвета."""
        show_color = type_name == "color_at_pixel"
        self.cond_preset_combo.setVisible(not show_color)
        self.cond_confidence_spin.setVisible(not show_color)
        self.cond_x_spin.setVisible(show_color)
        self.cond_y_spin.setVisible(show_color)
    
    def _on_loop_type_changed(self, type_name: str):
        """Показывает/скрывает поля для разных типов циклов."""
        show_iterations = type_name == "count"
        self.loop_iterations_spin.setVisible(show_iterations)
    
    def _load_action(self):
        """Загружает данные действия в форму."""
        if not self.action:
            return
        
        self.type_combo.setCurrentText(self.action.type.value)
        self.label_input.setText(self.action.label or "")
        self.desc_input.setText(self.action.description or "")
        self.enabled_check.setChecked(self.action.enabled)
        self.retry_count_spin.setValue(self.action.retry_count)
        self.retry_delay_spin.setValue(self.action.retry_delay)
        
        # Загружаем специфичные настройки в зависимости от типа
        # (упрощенная реализация)
    
    def get_action(self) -> Optional[Any]:
        """Возвращает созданное/отредактированное действие."""
        action_type = ActionType(self.type_combo.currentText())
        action_id = self.action.id if self.action else str(uuid.uuid4())[:8]
        
        offset = ClickOffset(
            enabled=self.offset_enabled.isChecked(),
            max_offset_x=self.offset_x_spin.value(),
            max_offset_y=self.offset_y_spin.value(),
        )
        
        match action_type:
            case ActionType.CLICK_ABSOLUTE:
                return ClickAbsoluteAction(
                    id=action_id,
                    type=action_type,
                    label=self.label_input.text(),
                    description=self.desc_input.text(),
                    enabled=self.enabled_check.isChecked(),
                    retry_count=self.retry_count_spin.value(),
                    retry_delay=self.retry_delay_spin.value(),
                    x=self.abs_x_spin.value(),
                    y=self.abs_y_spin.value(),
                    button=self.abs_button_combo.currentText(),
                    double_click=self.abs_double_check.isChecked(),
                    offset=offset,
                )
            case ActionType.CLICK_RELATIVE:
                preset_id = self.rel_preset_combo.currentData() or ""
                return ClickRelativeAction(
                    id=action_id,
                    type=action_type,
                    label=self.label_input.text(),
                    description=self.desc_input.text(),
                    enabled=self.enabled_check.isChecked(),
                    retry_count=self.retry_count_spin.value(),
                    retry_delay=self.retry_delay_spin.value(),
                    preset_id=preset_id,
                    x=self.rel_x_spin.value(),
                    y=self.rel_y_spin.value(),
                    button=self.rel_button_combo.currentText(),
                    double_click=self.rel_double_check.isChecked(),
                    offset=offset,
                )
            case ActionType.CLICK_IMAGE:
                preset_id = self.img_preset_combo.currentData() or ""
                return ClickImageAction(
                    id=action_id,
                    type=action_type,
                    label=self.label_input.text(),
                    description=self.desc_input.text(),
                    enabled=self.enabled_check.isChecked(),
                    retry_count=self.retry_count_spin.value(),
                    retry_delay=self.retry_delay_spin.value(),
                    preset_id=preset_id,
                    confidence_threshold=self.img_confidence_spin.value(),
                    click_position=self.img_position_combo.currentText(),
                    button=self.img_button_combo.currentText(),
                    double_click=self.img_double_check.isChecked(),
                    offset=offset,
                )
            case ActionType.DELAY:
                return DelayAction(
                    id=action_id,
                    type=action_type,
                    label=self.label_input.text(),
                    description=self.desc_input.text(),
                    enabled=self.enabled_check.isChecked(),
                    retry_count=self.retry_count_spin.value(),
                    retry_delay=self.retry_delay_spin.value(),
                    duration=self.delay_duration_spin.value(),
                )
            case ActionType.CONDITION:
                on_true = ConditionBranch(
                    action="goto" if self.cond_true_goto.text() else "continue",
                    target_label=self.cond_true_goto.text(),
                )
                on_false = ConditionBranch(
                    action="goto" if self.cond_false_goto.text() else "continue",
                    target_label=self.cond_false_goto.text(),
                )
                return ConditionAction(
                    id=action_id,
                    type=action_type,
                    label=self.label_input.text(),
                    description=self.desc_input.text(),
                    enabled=self.enabled_check.isChecked(),
                    retry_count=self.retry_count_spin.value(),
                    retry_delay=self.retry_delay_spin.value(),
                    condition_type=self.cond_type_combo.currentText(),
                    preset_id=self.cond_preset_combo.currentData() or "",
                    confidence_threshold=self.cond_confidence_spin.value(),
                    check_x=self.cond_x_spin.value(),
                    check_y=self.cond_y_spin.value(),
                    on_true=on_true,
                    on_false=on_false,
                )
            case ActionType.LOOP:
                return LoopAction(
                    id=action_id,
                    type=action_type,
                    label=self.label_input.text(),
                    description=self.desc_input.text(),
                    enabled=self.enabled_check.isChecked(),
                    retry_count=self.retry_count_spin.value(),
                    retry_delay=self.retry_delay_spin.value(),
                    loop_type=self.loop_type_combo.currentText(),
                    iterations=self.loop_iterations_spin.value(),
                    max_iterations=self.loop_max_spin.value(),
                )
            case ActionType.GOTO:
                return GotoAction(
                    id=action_id,
                    type=action_type,
                    label=self.label_input.text(),
                    description=self.desc_input.text(),
                    enabled=self.enabled_check.isChecked(),
                    retry_count=self.retry_count_spin.value(),
                    retry_delay=self.retry_delay_spin.value(),
                    target_label=self.goto_target_input.text(),
                )
            case ActionType.STATE_CHECK:
                on_unchanged = ConditionBranch(
                    action="goto" if self.state_unchanged_goto.text() else "continue",
                    target_label=self.state_unchanged_goto.text(),
                )
                on_changed = ConditionBranch(
                    action="goto" if self.state_changed_goto.text() else "continue",
                    target_label=self.state_changed_goto.text(),
                )
                return StateCheckAction(
                    id=action_id,
                    type=action_type,
                    label=self.label_input.text(),
                    description=self.desc_input.text(),
                    enabled=self.enabled_check.isChecked(),
                    retry_count=self.retry_count_spin.value(),
                    retry_delay=self.retry_delay_spin.value(),
                    area_type=self.state_area_type_combo.currentText(),
                    area_x=self.state_x_spin.value(),
                    area_y=self.state_y_spin.value(),
                    area_width=self.state_w_spin.value(),
                    area_height=self.state_h_spin.value(),
                    wait_duration=self.state_wait_spin.value(),
                    comparison_threshold=self.state_threshold_spin.value(),
                    unchanged_required=self.state_unchanged_spin.value(),
                    changed_allowed=self.state_changed_spin.value(),
                    on_unchanged=on_unchanged,
                    on_changed=on_changed,
                )
            case _:
                return None


class CVRecognitionWidget(QWidget):
    """Виджет для CV распознавания областей на экране по пресетам изображений."""
    
    def __init__(self, 
                 preset_storage: ScreenshotPresetStorage,
                 cv_matcher: CVMatcher):
        super().__init__()
        self.preset_storage = preset_storage
        self.cv_matcher = cv_matcher
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING)
        layout.setContentsMargins(ModernStyle.PADDING, ModernStyle.PADDING,
                                   ModernStyle.PADDING, ModernStyle.PADDING)
        
        # Заголовок
        title = QLabel("🔍 CV Распознавание областей")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Описание
        description = QLabel(
            "Дважды кликните на пресет для поиска области на экране, совпадающей с изображением.\n"
            "Найденная область будет подсвечена белой рамкой на черном фоне."
        )
        description.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(description)
        
        # Настройки уверенности
        settings_card = QFrame()
        settings_card.setObjectName("card")
        settings_layout = QVBoxLayout(settings_card)
        
        settings_title = QLabel("⚙️ Настройки распознавания")
        settings_title.setObjectName("sectionTitle")
        settings_layout.addWidget(settings_title)
        
        confidence_layout = QHBoxLayout()
        confidence_label = QLabel("Порог уверенности:")
        self.confidence_input = QDoubleSpinBox()
        self.confidence_input.setRange(0.1, 1.0)
        self.confidence_input.setSingleStep(0.05)
        self.confidence_input.setValue(self.cv_matcher._confidence_threshold)
        self.confidence_input.setToolTip("Минимальная уверенность для совпадения (0.1 - 1.0)")
        confidence_layout.addWidget(confidence_label)
        confidence_layout.addWidget(self.confidence_input)
        confidence_layout.addStretch()
        settings_layout.addLayout(confidence_layout)
        
        layout.addWidget(settings_card)
        
        # Поиск пресетов
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск пресетов изображений...")
        self.search_input.textChanged.connect(self._search_presets)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Таблица пресетов
        self.presets_table = QTableWidget()
        self.presets_table.setColumnCount(4)
        self.presets_table.setHorizontalHeaderLabels([
            "Имя", "ID", "Размер изображения", "Описание"
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
        self.presets_table.cellDoubleClicked.connect(self._on_preset_double_clicked)
        layout.addWidget(self.presets_table)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.find_btn = QPushButton("🔍 Найти область")
        self.find_btn.clicked.connect(self._find_area)
        buttons_layout.addWidget(self.find_btn)
        
        self.refresh_btn = QPushButton("🔄 Обновить список")
        self.refresh_btn.setObjectName("secondaryBtn")
        self.refresh_btn.clicked.connect(self._load_presets)
        buttons_layout.addWidget(self.refresh_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Статус
        self.status_label = QLabel("")
        self.status_label.setObjectName("fieldLabel")
        layout.addWidget(self.status_label)
        
        # Загружаем пресеты
        self._load_presets()
    
    def _load_presets(self):
        """Загружает пресеты в таблицу."""
        self.presets_table.setRowCount(0)
        presets = self.preset_storage.get_all_presets()
        
        for preset in presets:
            # Проверяем, существует ли файл скриншота
            screenshot_path = Path(preset.screenshot_path)
            if not screenshot_path.exists():
                continue
            
            row = self.presets_table.rowCount()
            self.presets_table.insertRow(row)
            
            item = QTableWidgetItem(preset.name)
            item.setData(Qt.ItemDataRole.UserRole, preset.id)
            self.presets_table.setItem(row, 0, item)
            
            self.presets_table.setItem(row, 1, QTableWidgetItem(preset.id))
            
            # Получаем размеры изображения
            try:
                from PIL import Image
                with Image.open(screenshot_path) as img:
                    size_text = f"{img.width} x {img.height}"
            except Exception:
                size_text = "Неизвестно"
            self.presets_table.setItem(row, 2, QTableWidgetItem(size_text))
            
            self.presets_table.setItem(row, 3, QTableWidgetItem(preset.description or ""))
    
    def _search_presets(self, text: str):
        """Ищет пресеты."""
        self.presets_table.setRowCount(0)
        presets = self.preset_storage.search_presets(text)
        
        for preset in presets:
            screenshot_path = Path(preset.screenshot_path)
            if not screenshot_path.exists():
                continue
            
            row = self.presets_table.rowCount()
            self.presets_table.insertRow(row)
            
            item = QTableWidgetItem(preset.name)
            item.setData(Qt.ItemDataRole.UserRole, preset.id)
            self.presets_table.setItem(row, 0, item)
            
            self.presets_table.setItem(row, 1, QTableWidgetItem(preset.id))
            
            try:
                from PIL import Image
                with Image.open(screenshot_path) as img:
                    size_text = f"{img.width} x {img.height}"
            except Exception:
                size_text = "Неизвестно"
            self.presets_table.setItem(row, 2, QTableWidgetItem(size_text))
            
            self.presets_table.setItem(row, 3, QTableWidgetItem(preset.description or ""))
    
    def _get_selected_preset(self) -> ScreenshotPreset | None:
        """Получает выбранный пресет."""
        selected_rows = self.presets_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        preset_id = self.presets_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return self.preset_storage.get_preset(preset_id)
    
    def _on_preset_double_clicked(self, row: int, column: int):
        """Обработчик двойного клика по пресету."""
        self._find_area()
    
    def _find_area(self):
        """Ищет область на экране по выбранному пресету."""
        preset = self._get_selected_preset()
        if not preset:
            QMessageBox.warning(self, "Предупреждение", "Выберите пресет!")
            return
        
        screenshot_path = Path(preset.screenshot_path)
        if not screenshot_path.exists():
            QMessageBox.warning(
                self, "Ошибка",
                f"Файл скриншота не найден: {preset.screenshot_path}"
            )
            return
        
        # Получаем порог уверенности из настроек
        confidence_threshold = self.confidence_input.value()
        
        self.status_label.setText(f"🔄 Поиск области для '{preset.name}'...")
        self.repaint()
        
        try:
            result = self.cv_matcher.find_match(
                preset_image_path=str(screenshot_path),
                preset_id=preset.id,
                preset_name=preset.name,
                confidence_threshold=confidence_threshold,
            )
            
            if result:
                self.status_label.setText(
                    f"✅ Найдено! Уверенность: {result.confidence:.1%} "
                    f"(X: {result.x}, Y: {result.y})"
                )
                # Показываем превью с белой рамкой
                self.cv_matcher.preview_match(result)
            else:
                self.status_label.setText(
                    f"❌ Совпадение не найдено (порог: {confidence_threshold:.0%})"
                )
                QMessageBox.information(
                    self, "Результат",
                    f"Совпадение не найдено с уверенностью выше {confidence_threshold:.0%}.\n"
                    "Попробуйте снизить порог уверенности или обновить пресет."
                )
        except RuntimeError as e:
            self.status_label.setText(f"❌ Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")


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
        
        self.btn_window_selection = SidebarButton("🪟", "Приложения")
        self.btn_window_selection.setChecked(True)
        sidebar_layout.addWidget(self.btn_window_selection)
        self.nav_buttons.append(self.btn_window_selection)
        
        self.btn_screenshot_presets = SidebarButton("🎬", "Скриншоты")
        sidebar_layout.addWidget(self.btn_screenshot_presets)
        self.nav_buttons.append(self.btn_screenshot_presets)
        
        self.btn_cv_recognition = SidebarButton("🔍", "CV Распознавание")
        sidebar_layout.addWidget(self.btn_cv_recognition)
        self.nav_buttons.append(self.btn_cv_recognition)
        
        # Кнопка макросов
        self.btn_macros = SidebarButton("🎬", "Макросы")
        sidebar_layout.addWidget(self.btn_macros)
        self.nav_buttons.append(self.btn_macros)
        
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
        
        # Вкладка 2: Пресеты скриншотов
        self.screenshot_presets = ScreenshotPresetsWidget(
            self.screenshot_preset_storage,
            self.preset_storage,
            self.screenshot_manager,
            self.normalizer
        )
        self.content_stack.addWidget(self.screenshot_presets)
        
        # Вкладка 3: CV распознавание
        self.cv_matcher = CVMatcher()
        self.cv_recognition = CVRecognitionWidget(
            self.screenshot_preset_storage,
            self.cv_matcher
        )
        self.content_stack.addWidget(self.cv_recognition)
        
        # Вкладка 4: Макросы
        self.macro_storage = MacroStorage()
        self.macro_executor = MacroExecutor(
            window_manager=self.window_manager,
            normalizer=self.normalizer,
            preset_storage=self.preset_storage,
            screenshot_manager=self.screenshot_manager,
            cv_matcher=self.cv_matcher,
        )
        self.macros_widget = MacrosWidget(
            macro_storage=self.macro_storage,
            macro_executor=self.macro_executor,
            screenshot_preset_storage=self.screenshot_preset_storage,
            preset_storage=self.preset_storage,
        )
        self.content_stack.addWidget(self.macros_widget)
        
        main_layout.addWidget(self.content_stack)
        
        # Подключаем кнопки навигации
        self.btn_window_selection.clicked.connect(lambda: self._switch_tab(0))
        self.btn_screenshot_presets.clicked.connect(lambda: self._switch_tab(1))
        self.btn_cv_recognition.clicked.connect(lambda: self._switch_tab(2))
        self.btn_macros.clicked.connect(lambda: self._switch_tab(3))
    
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
