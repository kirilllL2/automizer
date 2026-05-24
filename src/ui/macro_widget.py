"""
UI модуль для управления макросами.
Содержит виджеты для просмотра, запуска макросов и отдельное окно для редактирования.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QScrollArea, QGridLayout,
    QSpacerItem, QSizePolicy, QMessageBox, QDialog, QDialogButtonBox,
    QFormLayout, QSpinBox, QComboBox, QLineEdit, QDoubleSpinBox,
    QListWidget, QListWidgetItem, QToolBar, QMenu, QAbstractItemView,
    QMainWindow, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction, QCursor

from src.macro import (
    MacroStorage, Macro, MacroAction, ActionType, create_action
)
from src.ui.main_window import ModernStyle, apply_modern_style


class ActionListWidget(QListWidget):
    """Список действий макроса с поддержкой Drag&Drop."""
    
    action_selected = pyqtSignal(MacroAction)
    action_double_clicked_signal = pyqtSignal(MacroAction)
    action_moved = pyqtSignal(int, int)  # from_index, to_index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.itemClicked.connect(self._on_item_clicked)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._actions: list[MacroAction] = []
    
    def set_actions(self, actions: list[MacroAction]):
        """Устанавливает список действий."""
        self.clear()
        self._actions = actions
        for action in actions:
            icon = "🖱️" if action.action_type == ActionType.CLICK else "⏱️"
            status = "✓" if action.enabled else "✗"
            item = QListWidgetItem(f"{icon} {status} {action.name}")
            item.setData(Qt.ItemDataRole.UserRole, action)
            self.addItem(item)
    
    def get_actions(self) -> list[MacroAction]:
        """Возвращает список действий."""
        return self._actions
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Обработка клика по элементу."""
        action = item.data(Qt.ItemDataRole.UserRole)
        if action:
            self.action_selected.emit(action)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Обработка двойного клика по элементу."""
        action = item.data(Qt.ItemDataRole.UserRole)
        if action:
            self.action_double_clicked_signal.emit(action)
    
    def dropEvent(self, event):
        """Обработка перетаскивания."""
        old_index = self.currentRow()
        super().dropEvent(event)
        new_index = self.currentRow()
        
        if old_index != -1 and new_index != -1 and old_index != new_index:
            # Перемещаем действие в списке
            action = self._actions.pop(old_index)
            self._actions.insert(new_index, action)
            self.action_moved.emit(old_index, new_index)


class MacrosWidget(QWidget):
    """Основной виджет управления макросами (вкладка)."""
    
    def __init__(self, storage: MacroStorage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING)
        layout.setContentsMargins(ModernStyle.PADDING, ModernStyle.PADDING,
                                   ModernStyle.PADDING, ModernStyle.PADDING)
        
        # Заголовок
        title = QLabel("🎬 Макросы")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Верхняя панель
        top_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self._load_macros)
        top_layout.addWidget(self.refresh_btn)
        
        self.new_macro_btn = QPushButton("➕ Новый макрос")
        self.new_macro_btn.clicked.connect(self._create_new_macro)
        top_layout.addWidget(self.new_macro_btn)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Таблица макросов
        self.macros_table = QTableWidget()
        self.macros_table.setColumnCount(4)
        self.macros_table.setHorizontalHeaderLabels([
            "Название", "Описание", "Действий", "Дата обновления"
        ])
        self.macros_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.macros_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.macros_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.macros_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.macros_table.itemDoubleClicked.connect(self._on_macro_double_clicked)
        layout.addWidget(self.macros_table)
        
        # Панель действий
        actions_card = QFrame()
        actions_card.setObjectName("card")
        actions_layout = QHBoxLayout(actions_card)
        
        self.run_btn = QPushButton("▶️ Запустить")
        self.run_btn.setObjectName("successBtn")
        self.run_btn.clicked.connect(self._run_macro)
        self.run_btn.setEnabled(False)
        actions_layout.addWidget(self.run_btn)
        
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.clicked.connect(self._edit_macro)
        self.edit_btn.setEnabled(False)
        actions_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._delete_macro)
        self.delete_btn.setEnabled(False)
        actions_layout.addWidget(self.delete_btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions_card)
        
        # Загружаем макросы
        self._load_macros()
    
    def _load_macros(self):
        """Загружает список макросов."""
        self.macros_table.setRowCount(0)
        macros = self.storage.list_macros()
        
        for macro in macros:
            row = self.macros_table.rowCount()
            self.macros_table.insertRow(row)
            
            self.macros_table.setItem(row, 0, QTableWidgetItem(macro.name))
            self.macros_table.setItem(row, 1, QTableWidgetItem(macro.description))
            self.macros_table.setItem(row, 2, QTableWidgetItem(str(len(macro.actions))))
            
            from datetime import datetime
            updated = datetime.fromtimestamp(macro.updated_at).strftime("%Y-%m-%d %H:%M")
            self.macros_table.setItem(row, 3, QTableWidgetItem(updated))
        
        self.macros_table.itemSelectionChanged.connect(self._on_macro_selected)
    
    def _on_macro_selected(self):
        """Выбран макрос в таблице."""
        selected = len(self.macros_table.selectedItems()) > 0
        self.edit_btn.setEnabled(selected)
        self.run_btn.setEnabled(selected)
        self.delete_btn.setEnabled(selected)
    
    def _on_macro_double_clicked(self, row: int, column: int):
        """Двойной клик по макросу - открываем редактор."""
        self._edit_macro()
    
    def _get_selected_macro(self) -> Macro | None:
        """Получает выбранный макрос."""
        selected_rows = self.macros_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        macro_id = self.macros_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Ищем макрос по названию (упрощенно)
        macro_name = self.macros_table.item(row, 0).text()
        for macro in self.storage.list_macros():
            if macro.name == macro_name:
                return macro
        
        return None
    
    def _create_new_macro(self):
        """Создает новый макрос."""
        from src.ui.macro_editor_window import MacroEditorWindow
        macro = self.storage.create_macro("Новый макрос", "")
        dialog = MacroEditorWindow(macro, self.storage, self)
        dialog.macro_saved.connect(self._load_macros)
        dialog.exec()
    
    def _edit_macro(self):
        """Редактирует выбранный макрос."""
        macro = self._get_selected_macro()
        if macro:
            from src.ui.macro_editor_window import MacroEditorWindow
            dialog = MacroEditorWindow(macro, self.storage, self)
            dialog.macro_saved.connect(self._load_macros)
            dialog.exec()
    
    def _run_macro(self):
        """Запускает выбранный макрос."""
        macro = self._get_selected_macro()
        if macro:
            reply = QMessageBox.question(
                self, "Запуск макроса",
                f"Запустить макрос '{macro.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Запуск в отдельном потоке будет добавлен позже
                success = self.storage.execute_macro(macro.id)
                if success:
                    QMessageBox.information(self, "Готово", "Макрос успешно выполнен")
                else:
                    QMessageBox.warning(self, "Ошибка", "При выполнении макроса произошла ошибка")
    
    def _delete_macro(self):
        """Удаляет выбранный макрос."""
        macro = self._get_selected_macro()
        if macro:
            reply = QMessageBox.question(
                self, "Удаление макроса",
                f"Вы уверены, что хотите удалить макрос '{macro.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.storage.delete_macro(macro.id)
                self._load_macros()

