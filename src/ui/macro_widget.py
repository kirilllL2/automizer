"""
UI модуль для управления макросами.
Содержит виджеты для просмотра, редактирования и запуска макросов.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QScrollArea, QGridLayout,
    QSpacerItem, QSizePolicy, QMessageBox, QDialog, QDialogButtonBox,
    QFormLayout, QSpinBox, QComboBox, QLineEdit, QDoubleSpinBox,
    QListWidget, QListWidgetItem, QToolBar, QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction, QCursor

from src.macro import (
    MacroStorage, Macro, MacroAction, ClickAction, DelayAction,
    ActionType, create_action
)
from src.ui.main_window import ModernStyle, apply_modern_style


class ActionListWidget(QListWidget):
    """Список действий макроса с поддержкой Drag&Drop."""
    
    action_selected = pyqtSignal(MacroAction)
    action_moved = pyqtSignal(int, int)  # from_index, to_index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.itemClicked.connect(self._on_item_clicked)
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


class ActionEditorWidget(QWidget):
    """Виджет редактирования параметров действия."""
    
    action_changed = pyqtSignal(MacroAction)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_action: MacroAction | None = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING)
        layout.setContentsMargins(ModernStyle.PADDING, ModernStyle.PADDING,
                                   ModernStyle.PADDING, ModernStyle.PADDING)
        
        # Карточка редактора
        editor_card = QFrame()
        editor_card.setObjectName("card")
        editor_layout = QVBoxLayout(editor_card)
        
        title = QLabel("⚙️ Редактирование действия")
        title.setObjectName("sectionTitle")
        editor_layout.addWidget(title)
        
        # Форма редактирования
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(8)
        
        # Название действия
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название действия")
        self.name_input.textChanged.connect(self._on_name_changed)
        self.form_layout.addRow("Название:", self.name_input)
        
        # Статус (включено/выключено)
        self.enabled_combo = QComboBox()
        self.enabled_combo.addItems(["Включено", "Выключено"])
        self.enabled_combo.currentIndexChanged.connect(self._on_enabled_changed)
        self.form_layout.addRow("Статус:", self.enabled_combo)
        
        # Контейнер для специфичных полей
        self.specific_fields_widget = QWidget()
        self.specific_layout = QVBoxLayout(self.specific_fields_widget)
        self.specific_layout.setContentsMargins(0, 8, 0, 0)
        self.form_layout.addRow("", self.specific_fields_widget)
        
        editor_layout.addLayout(self.form_layout)
        layout.addWidget(editor_card)
        
        # Скрываем редактор пока ничего не выбрано
        self.setEnabled(False)
    
    def set_action(self, action: MacroAction | None):
        """Устанавливает действие для редактирования."""
        self.current_action = action
        
        if action is None:
            self.setEnabled(False)
            return
        
        self.setEnabled(True)
        self.name_input.setText(action.name)
        self.enabled_combo.setCurrentIndex(0 if action.enabled else 1)
        
        # Очищаем специфичные поля
        while self.specific_layout.count():
            item = self.specific_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Добавляем поля в зависимости от типа действия
        if isinstance(action, ClickAction):
            self._setup_click_fields(action)
        elif isinstance(action, DelayAction):
            self._setup_delay_fields(action)
    
    def _setup_click_fields(self, action: ClickAction):
        """Настраивает поля для действия клика."""
        grid = QGridLayout()
        grid.setSpacing(8)
        
        x_label = QLabel("X:")
        x_label.setObjectName("fieldLabel")
        self.x_input = QSpinBox()
        self.x_input.setRange(-10000, 10000)
        self.x_input.setValue(action.x)
        self.x_input.valueChanged.connect(self._on_click_params_changed)
        
        y_label = QLabel("Y:")
        y_label.setObjectName("fieldLabel")
        self.y_input = QSpinBox()
        self.y_input.setRange(-10000, 10000)
        self.y_input.setValue(action.y)
        self.y_input.valueChanged.connect(self._on_click_params_changed)
        
        grid.addWidget(x_label, 0, 0)
        grid.addWidget(self.x_input, 0, 1)
        grid.addWidget(y_label, 1, 0)
        grid.addWidget(self.y_input, 1, 1)
        
        self.specific_layout.addLayout(grid)
    
    def _setup_delay_fields(self, action: DelayAction):
        """Настраивает поля для действия задержки."""
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0.1, 3600.0)
        self.duration_input.setValue(action.duration)
        self.duration_input.setSuffix(" сек.")
        self.duration_input.valueChanged.connect(self._on_delay_params_changed)
        
        self.specific_layout.addWidget(self.duration_input)
    
    def _on_name_changed(self, text: str):
        if self.current_action:
            self.current_action.name = text
            self.action_changed.emit(self.current_action)
    
    def _on_enabled_changed(self, index: int):
        if self.current_action:
            self.current_action.enabled = (index == 0)
            self.action_changed.emit(self.current_action)
    
    def _on_click_params_changed(self):
        if self.current_action and isinstance(self.current_action, ClickAction):
            self.current_action.x = self.x_input.value()
            self.current_action.y = self.y_input.value()
            self.current_action.parameters = {"x": self.current_action.x, "y": self.current_action.y}
            self.action_changed.emit(self.current_action)
    
    def _on_delay_params_changed(self):
        if self.current_action and isinstance(self.current_action, DelayAction):
            self.current_action.duration = self.duration_input.value()
            self.current_action.parameters = {"duration": self.current_action.duration}
            self.action_changed.emit(self.current_action)


class MacroEditorWidget(QWidget):
    """Виджет редактирования макроса."""
    
    macro_saved = pyqtSignal()
    macro_deleted = pyqtSignal(str)
    
    def __init__(self, storage: MacroStorage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.current_macro: Macro | None = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING)
        layout.setContentsMargins(ModernStyle.PADDING, ModernStyle.PADDING,
                                   ModernStyle.PADDING, ModernStyle.PADDING)
        
        # Заголовок
        title = QLabel("📝 Редактор макроса")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Информация о макросе
        info_card = QFrame()
        info_card.setObjectName("card")
        info_layout = QGridLayout(info_card)
        info_layout.setSpacing(8)
        
        info_layout.addWidget(QLabel("Название:"), 0, 0)
        self.macro_name_input = QLineEdit()
        self.macro_name_input.setPlaceholderText("Название макроса")
        info_layout.addWidget(self.macro_name_input, 0, 1)
        
        info_layout.addWidget(QLabel("Описание:"), 1, 0)
        self.macro_desc_input = QLineEdit()
        self.macro_desc_input.setPlaceholderText("Описание макроса")
        info_layout.addWidget(self.macro_desc_input, 1, 1)
        
        layout.addWidget(info_card)
        
        # Список действий
        actions_card = QFrame()
        actions_card.setObjectName("card")
        actions_layout = QVBoxLayout(actions_card)
        
        actions_title = QLabel("📋 Действия")
        actions_title.setObjectName("sectionTitle")
        actions_layout.addWidget(actions_title)
        
        # Список действий
        self.action_list = ActionListWidget()
        self.action_list.setMinimumHeight(200)
        self.action_list.action_selected.connect(self._on_action_selected)
        self.action_list.action_moved.connect(self._on_action_moved)
        actions_layout.addWidget(self.action_list)
        
        # Кнопки управления действиями
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.add_click_btn = QPushButton("🖱️ Добавить клик")
        self.add_click_btn.clicked.connect(self._add_click_action)
        btn_layout.addWidget(self.add_click_btn)
        
        self.add_delay_btn = QPushButton("⏱️ Добавить задержку")
        self.add_delay_btn.clicked.connect(self._add_delay_action)
        btn_layout.addWidget(self.add_delay_btn)
        
        btn_layout.addStretch()
        
        self.move_up_btn = QPushButton("⬆️ Вверх")
        self.move_up_btn.setObjectName("secondaryBtn")
        self.move_up_btn.clicked.connect(self._move_action_up)
        btn_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("⬇️ Вниз")
        self.move_down_btn.setObjectName("secondaryBtn")
        self.move_down_btn.clicked.connect(self._move_action_down)
        btn_layout.addWidget(self.move_down_btn)
        
        self.delete_action_btn = QPushButton("🗑️ Удалить")
        self.delete_action_btn.setObjectName("dangerBtn")
        self.delete_action_btn.clicked.connect(self._delete_action)
        btn_layout.addWidget(self.delete_action_btn)
        
        actions_layout.addLayout(btn_layout)
        layout.addWidget(actions_card)
        
        # Редактор действия
        self.action_editor = ActionEditorWidget()
        self.action_editor.action_changed.connect(self._on_action_changed)
        layout.addWidget(self.action_editor)
        
        # Кнопки сохранения
        save_layout = QHBoxLayout()
        save_layout.setSpacing(12)
        
        self.save_btn = QPushButton("💾 Сохранить макрос")
        self.save_btn.setObjectName("successBtn")
        self.save_btn.clicked.connect(self._save_macro)
        save_layout.addWidget(self.save_btn)
        
        self.delete_macro_btn = QPushButton("🗑️ Удалить макрос")
        self.delete_macro_btn.setObjectName("dangerBtn")
        self.delete_macro_btn.clicked.connect(self._delete_macro)
        save_layout.addWidget(self.delete_macro_btn)
        
        save_layout.addStretch()
        
        self.cancel_btn = QPushButton("✕ Отмена")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self._cancel_edit)
        save_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(save_layout)
        
        # Скрываем редактор пока макрос не выбран
        self._set_editing_enabled(False)
    
    def _set_editing_enabled(self, enabled: bool):
        """Включает/выключает режим редактирования."""
        self.macro_name_input.setEnabled(enabled)
        self.macro_desc_input.setEnabled(enabled)
        self.add_click_btn.setEnabled(enabled)
        self.add_delay_btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)
        self.delete_macro_btn.setEnabled(enabled)
    
    def load_macro(self, macro: Macro):
        """Загружает макрос для редактирования."""
        self.current_macro = macro
        self.macro_name_input.setText(macro.name)
        self.macro_desc_input.setText(macro.description)
        self.action_list.set_actions(macro.actions)
        self.action_editor.set_action(None)
        self._set_editing_enabled(True)
    
    def clear(self):
        """Очищает редактор."""
        self.current_macro = None
        self.macro_name_input.clear()
        self.macro_desc_input.clear()
        self.action_list.clear()
        self.action_editor.set_action(None)
        self._set_editing_enabled(False)
    
    def _on_action_selected(self, action: MacroAction):
        """Выбрано действие для редактирования."""
        self.action_editor.set_action(action)
    
    def _on_action_changed(self, action: MacroAction):
        """Действие изменено."""
        # Обновляем отображение в списке
        current_row = self.action_list.currentRow()
        if current_row >= 0:
            item = self.action_list.item(current_row)
            icon = "🖱️" if action.action_type == ActionType.CLICK else "⏱️"
            status = "✓" if action.enabled else "✗"
            item.setText(f"{icon} {status} {action.name}")
    
    def _on_action_moved(self, from_index: int, to_index: int):
        """Действие перемещено."""
        if self.current_macro:
            self.current_macro.move_action(
                self.current_macro.actions[from_index].id,
                to_index
            )
            self.action_list.set_actions(self.current_macro.actions)
    
    def _add_click_action(self):
        """Добавляет действие клика."""
        if not self.current_macro:
            return
        
        action = create_action(ActionType.CLICK, "Клик", x=100, y=100)
        self.current_macro.add_action(action)
        self.action_list.set_actions(self.current_macro.actions)
    
    def _add_delay_action(self):
        """Добавляет действие задержки."""
        if not self.current_macro:
            return
        
        action = create_action(ActionType.DELAY, "Задержка", duration=1.0)
        self.current_macro.add_action(action)
        self.action_list.set_actions(self.current_macro.actions)
    
    def _move_action_up(self):
        """Перемещает действие вверх."""
        current_row = self.action_list.currentRow()
        if current_row > 0 and self.current_macro:
            action = self.current_macro.actions[current_row]
            self.current_macro.move_action(action.id, current_row - 1)
            self.action_list.set_actions(self.current_macro.actions)
            self.action_list.setCurrentRow(current_row - 1)
    
    def _move_action_down(self):
        """Перемещает действие вниз."""
        current_row = self.action_list.currentRow()
        if current_row >= 0 and self.current_macro and current_row < len(self.current_macro.actions) - 1:
            action = self.current_macro.actions[current_row]
            self.current_macro.move_action(action.id, current_row + 1)
            self.action_list.set_actions(self.current_macro.actions)
            self.action_list.setCurrentRow(current_row + 1)
    
    def _delete_action(self):
        """Удаляет выбранное действие."""
        current_row = self.action_list.currentRow()
        if current_row >= 0 and self.current_macro:
            action = self.current_macro.actions[current_row]
            self.current_macro.remove_action(action.id)
            self.action_list.set_actions(self.current_macro.actions)
            self.action_editor.set_action(None)
    
    def _save_macro(self):
        """Сохраняет макрос."""
        if not self.current_macro:
            return
        
        self.current_macro.name = self.macro_name_input.text()
        self.current_macro.description = self.macro_desc_input.text()
        self.current_macro.actions = self.action_list.get_actions()
        
        self.storage.update_macro(self.current_macro)
        self.macro_saved.emit()
    
    def _delete_macro(self):
        """Удаляет макрос."""
        if not self.current_macro:
            return
        
        reply = QMessageBox.question(
            self, "Удаление макроса",
            f"Вы уверены, что хотите удалить макрос '{self.current_macro.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.delete_macro(self.current_macro.id)
            self.macro_deleted.emit(self.current_macro.id)
            self.clear()
    
    def _cancel_edit(self):
        """Отменяет редактирование."""
        self.clear()


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
        
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.clicked.connect(self._edit_macro)
        self.edit_btn.setEnabled(False)
        actions_layout.addWidget(self.edit_btn)
        
        self.run_btn = QPushButton("▶️ Запустить")
        self.run_btn.setObjectName("successBtn")
        self.run_btn.clicked.connect(self._run_macro)
        self.run_btn.setEnabled(False)
        actions_layout.addWidget(self.run_btn)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._delete_macro)
        self.delete_btn.setEnabled(False)
        actions_layout.addWidget(self.delete_btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions_card)
        
        # Виджет редактора (скрыт по умолчанию)
        self.editor_widget = MacroEditorWidget(self.storage)
        self.editor_widget.macro_saved.connect(self._on_macro_saved)
        self.editor_widget.macro_deleted.connect(self._on_macro_deleted)
        self.editor_widget.hide()
        layout.addWidget(self.editor_widget)
        
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
        macro = self.storage.create_macro("Новый макрос", "")
        self.editor_widget.load_macro(macro)
        self.editor_widget.show()
        self.macros_table.hide()
        self.refresh_btn.hide()
        self.new_macro_btn.hide()
        self.edit_btn.hide()
        self.run_btn.hide()
        self.delete_btn.hide()
    
    def _edit_macro(self):
        """Редактирует выбранный макрос."""
        macro = self._get_selected_macro()
        if macro:
            self.editor_widget.load_macro(macro)
            self.editor_widget.show()
            self.macros_table.hide()
            self.refresh_btn.hide()
            self.new_macro_btn.hide()
            self.edit_btn.hide()
            self.run_btn.hide()
            self.delete_btn.hide()
    
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
    
    def _on_macro_saved(self):
        """Макрос сохранен."""
        self.editor_widget.hide()
        self.macros_table.show()
        self.refresh_btn.show()
        self.new_macro_btn.show()
        self.edit_btn.show()
        self.run_btn.show()
        self.delete_btn.show()
        self._load_macros()
    
    def _on_macro_deleted(self, macro_id: str):
        """Макрос удален."""
        self._load_macros()
        self.editor_widget.hide()
        self.macros_table.show()
        self.refresh_btn.show()
        self.new_macro_btn.show()
        self.edit_btn.show()
        self.run_btn.show()
        self.delete_btn.show()
