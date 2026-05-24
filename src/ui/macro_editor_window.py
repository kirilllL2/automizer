"""
Отдельное окно для редактирования макросов.
Открывается в модальном режиме для удобного редактирования действий.
"""

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QFormLayout, QSpinBox, QComboBox, QLineEdit, 
    QDoubleSpinBox, QListWidget, QListWidgetItem, QAbstractItemView,
    QMessageBox, QSplitter, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QAction

from src.macro import (
    Macro, MacroAction, ClickAction, DelayAction,
    ActionType, create_action
)
from src.ui.main_window import ModernStyle, apply_modern_style


class ActionListWidget(QListWidget):
    """Список действий макроса с поддержкой Drag&Drop и контекстным меню."""
    
    action_selected = pyqtSignal(MacroAction)
    action_double_clicked_signal = pyqtSignal(MacroAction)
    action_moved = pyqtSignal(int, int)
    action_added = pyqtSignal(ActionType)
    action_delete_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.itemClicked.connect(self._on_item_clicked)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._actions: list[MacroAction] = []
        self._setup_context_menu()
    
    def _setup_context_menu(self):
        """Настраивает контекстное меню."""
        self.context_menu = QMenu(self)
        
        add_click_action = QAction("🖱️ Добавить клик", self)
        add_click_action.triggered.connect(lambda: self.action_added.emit(ActionType.CLICK))
        self.context_menu.addAction(add_click_action)
        
        add_delay_action = QAction("⏱️ Добавить задержку", self)
        add_delay_action.triggered.connect(lambda: self.action_added.emit(ActionType.DELAY))
        self.context_menu.addAction(add_delay_action)
        
        self.context_menu.addSeparator()
        
        delete_action = QAction("🗑️ Удалить выбранное", self)
        delete_action.triggered.connect(lambda: self.action_delete_requested.emit())
        self.context_menu.addAction(delete_action)
    
    def _show_context_menu(self, pos):
        """Показывает контекстное меню."""
        self.context_menu.exec(self.mapToGlobal(pos))
    
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
        """Обработка двойного клика по элементу - открываем редактор."""
        action = item.data(Qt.ItemDataRole.UserRole)
        if action:
            self.action_double_clicked_signal.emit(action)
    
    def dropEvent(self, event):
        """Обработка перетаскивания."""
        old_index = self.currentRow()
        super().dropEvent(event)
        new_index = self.currentRow()
        
        if old_index != -1 and new_index != -1 and old_index != new_index:
            action = self._actions.pop(old_index)
            self._actions.insert(new_index, action)
            self.action_moved.emit(old_index, new_index)


class ActionEditorDialog(QDialog):
    """Диалоговое окно для редактирования параметров действия."""
    
    action_changed = pyqtSignal(MacroAction)
    
    def __init__(self, action: MacroAction, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование действия")
        self.setMinimumSize(400, 300)
        self.current_action = action
        self._setup_ui()
        apply_modern_style(self)
    
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
        self.name_input.setText(self.current_action.name)
        self.name_input.textChanged.connect(self._on_name_changed)
        self.form_layout.addRow("Название:", self.name_input)
        
        # Статус (включено/выключено)
        self.enabled_combo = QComboBox()
        self.enabled_combo.addItems(["Включено", "Выключено"])
        self.enabled_combo.setCurrentIndex(0 if self.current_action.enabled else 1)
        self.enabled_combo.currentIndexChanged.connect(self._on_enabled_changed)
        self.form_layout.addRow("Статус:", self.enabled_combo)
        
        # Контейнер для специфичных полей
        self.specific_fields_widget = QWidget()
        self.specific_layout = QVBoxLayout(self.specific_fields_widget)
        self.specific_layout.setContentsMargins(0, 8, 0, 0)
        self.form_layout.addRow("", self.specific_fields_widget)
        
        editor_layout.addLayout(self.form_layout)
        layout.addWidget(editor_card)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Добавляем поля в зависимости от типа действия
        if isinstance(self.current_action, ClickAction):
            self._setup_click_fields()
        elif isinstance(self.current_action, DelayAction):
            self._setup_delay_fields()
    
    def _setup_click_fields(self):
        """Настраивает поля для действия клика."""
        grid = QGridLayout()
        grid.setSpacing(8)
        
        x_label = QLabel("X:")
        x_label.setObjectName("fieldLabel")
        self.x_input = QSpinBox()
        self.x_input.setRange(-10000, 10000)
        self.x_input.setValue(self.current_action.x)
        self.x_input.valueChanged.connect(self._on_click_params_changed)
        
        y_label = QLabel("Y:")
        y_label.setObjectName("fieldLabel")
        self.y_input = QSpinBox()
        self.y_input.setRange(-10000, 10000)
        self.y_input.setValue(self.current_action.y)
        self.y_input.valueChanged.connect(self._on_click_params_changed)
        
        grid.addWidget(x_label, 0, 0)
        grid.addWidget(self.x_input, 0, 1)
        grid.addWidget(y_label, 1, 0)
        grid.addWidget(self.y_input, 1, 1)
        
        self.specific_layout.addLayout(grid)
    
    def _setup_delay_fields(self):
        """Настраивает поля для действия задержки."""
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0.1, 3600.0)
        self.duration_input.setValue(self.current_action.duration)
        self.duration_input.setSuffix(" сек.")
        self.duration_input.valueChanged.connect(self._on_delay_params_changed)
        
        self.specific_layout.addWidget(self.duration_input)
    
    def _on_name_changed(self, text: str):
        self.current_action.name = text
        self.action_changed.emit(self.current_action)
    
    def _on_enabled_changed(self, index: int):
        self.current_action.enabled = (index == 0)
        self.action_changed.emit(self.current_action)
    
    def _on_click_params_changed(self):
        if isinstance(self.current_action, ClickAction):
            self.current_action.x = self.x_input.value()
            self.current_action.y = self.y_input.value()
            self.current_action.parameters = {"x": self.current_action.x, "y": self.current_action.y}
            self.action_changed.emit(self.current_action)
    
    def _on_delay_params_changed(self):
        if isinstance(self.current_action, DelayAction):
            self.current_action.duration = self.duration_input.value()
            self.current_action.parameters = {"duration": self.current_action.duration}
            self.action_changed.emit(self.current_action)


class MacroEditorWindow(QDialog):
    """Отдельное окно для редактирования макроса."""
    
    macro_saved = pyqtSignal()
    
    def __init__(self, macro: Macro, storage: MacroStorage, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Редактор макроса: {macro.name}")
        self.setMinimumSize(900, 700)
        self.macro = macro
        self.storage = storage
        self._setup_ui()
        apply_modern_style(self)
    
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
        self.macro_name_input.setText(self.macro.name)
        info_layout.addWidget(self.macro_name_input, 0, 1)
        
        info_layout.addWidget(QLabel("Описание:"), 1, 0)
        self.macro_desc_input = QLineEdit()
        self.macro_desc_input.setPlaceholderText("Описание макроса")
        self.macro_desc_input.setText(self.macro.description)
        info_layout.addWidget(self.macro_desc_input, 1, 1)
        
        layout.addWidget(info_card)
        
        # Разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - список действий
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        actions_title = QLabel("📋 Действия (перетаскивайте для перемещения)")
        actions_title.setObjectName("sectionTitle")
        left_layout.addWidget(actions_title)
        
        # Список действий
        self.action_list = ActionListWidget()
        self.action_list.setMinimumWidth(300)
        self.action_list.action_selected.connect(self._on_action_selected)
        self.action_list.action_double_clicked_signal.connect(self._edit_action_dialog)
        self.action_list.action_moved.connect(self._on_action_moved)
        self.action_list.action_added.connect(self._add_action_by_type)
        self.action_list.action_delete_requested.connect(self._delete_action)
        left_layout.addWidget(self.action_list)
        
        # Кнопки управления действиями (компактные)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        
        self.add_btn = QPushButton("+")
        self.add_btn.setObjectName("secondaryBtn")
        self.add_btn.setToolTip("Добавить действие (ПКМ для выбора)")
        self.add_btn.setFixedWidth(30)
        btn_layout.addWidget(self.add_btn)
        
        self.move_up_btn = QPushButton("⬆")
        self.move_up_btn.setObjectName("secondaryBtn")
        self.move_up_btn.setToolTip("Переместить вверх")
        self.move_up_btn.setFixedWidth(30)
        self.move_up_btn.clicked.connect(self._move_action_up)
        btn_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("⬇")
        self.move_down_btn.setObjectName("secondaryBtn")
        self.move_down_btn.setToolTip("Переместить вниз")
        self.move_down_btn.setFixedWidth(30)
        self.move_down_btn.clicked.connect(self._move_action_down)
        btn_layout.addWidget(self.move_down_btn)
        
        self.delete_action_btn = QPushButton("🗑")
        self.delete_action_btn.setObjectName("dangerBtn")
        self.delete_action_btn.setToolTip("Удалить действие")
        self.delete_action_btn.setFixedWidth(30)
        self.delete_action_btn.clicked.connect(self._delete_action)
        btn_layout.addWidget(self.delete_action_btn)
        
        hint_label = QLabel("💡 ПКМ для добавления/удаления, двойной клик для редактирования")
        hint_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; font-size: 11px;")
        btn_layout.addWidget(hint_label)
        
        btn_layout.addStretch()
        
        left_layout.addLayout(btn_layout)
        splitter.addWidget(left_widget)
        
        # Правая панель - детали действия
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        details_title = QLabel("ℹ️ Детали действия")
        details_title.setObjectName("sectionTitle")
        right_layout.addWidget(details_title)
        
        self.details_label = QLabel("Выберите действие для просмотра деталей\n\nДвойной клик для редактирования")
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; padding: 20px;")
        right_layout.addWidget(self.details_label)
        
        right_layout.addStretch()
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        
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
        
        self.cancel_btn = QPushButton("✕ Закрыть")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.close)
        save_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(save_layout)
        
        # Загружаем действия
        self.action_list.set_actions(self.macro.actions)
    
    def _on_action_selected(self, action: MacroAction):
        """Выбрано действие - показываем детали."""
        icon = "🖱️" if action.action_type == ActionType.CLICK else "⏱️"
        status = "Включено" if action.enabled else "Выключено"
        
        details = f"<h3>{icon} {action.name}</h3>"
        details += f"<p><b>Тип:</b> {action.action_type.value}</p>"
        details += f"<p><b>Статус:</b> {status}</p>"
        
        if isinstance(action, ClickAction):
            details += f"<p><b>Координаты:</b> X={action.x}, Y={action.y}</p>"
        elif isinstance(action, DelayAction):
            details += f"<p><b>Длительность:</b> {action.duration} сек.</p>"
        
        details += "<p style='margin-top: 20px; color: #7f8af4;'>💡 Двойной клик для редактирования</p>"
        
        self.details_label.setText(details)
        self.details_label.setStyleSheet(f"""
            color: {ModernStyle.TEXT_PRIMARY}; 
            padding: 20px; 
            background-color: {ModernStyle.BG_PRIMARY};
            border-radius: {ModernStyle.BORDER_RADIUS}px;
        """)
    
    def _edit_action_dialog(self, action: MacroAction):
        """Открывает диалог редактирования действия."""
        dialog = ActionEditorDialog(action, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Обновляем отображение в списке
            self.action_list.set_actions(self.macro.actions)
    
    def _on_action_moved(self, from_index: int, to_index: int):
        """Действие перемещено."""
        self.macro.move_action(
            self.macro.actions[from_index].id,
            to_index
        )
        self.action_list.set_actions(self.macro.actions)
    
    def _add_action_by_type(self, action_type: ActionType):
        """Добавляет действие указанного типа."""
        if action_type == ActionType.CLICK:
            action = create_action(ActionType.CLICK, "Клик", x=100, y=100)
        else:
            action = create_action(ActionType.DELAY, "Задержка", duration=1.0)
        self.macro.add_action(action)
        self.action_list.set_actions(self.macro.actions)
    
    def _move_action_up(self):
        """Перемещает действие вверх."""
        current_row = self.action_list.currentRow()
        if current_row > 0:
            action = self.macro.actions[current_row]
            self.macro.move_action(action.id, current_row - 1)
            self.action_list.set_actions(self.macro.actions)
            self.action_list.setCurrentRow(current_row - 1)
    
    def _move_action_down(self):
        """Перемещает действие вниз."""
        current_row = self.action_list.currentRow()
        if current_row >= 0 and current_row < len(self.macro.actions) - 1:
            action = self.macro.actions[current_row]
            self.macro.move_action(action.id, current_row + 1)
            self.action_list.set_actions(self.macro.actions)
            self.action_list.setCurrentRow(current_row + 1)
    
    def _delete_action(self):
        """Удаляет выбранное действие."""
        current_row = self.action_list.currentRow()
        if current_row >= 0:
            action = self.macro.actions[current_row]
            self.macro.remove_action(action.id)
            self.action_list.set_actions(self.macro.actions)
            self.details_label.setText("Выберите действие для просмотра деталей\n\nДвойной клик для редактирования")
            self.details_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; padding: 20px;")
    
    def _save_macro(self):
        """Сохраняет макрос."""
        self.macro.name = self.macro_name_input.text()
        self.macro.description = self.macro_desc_input.text()
        self.macro.actions = self.action_list.get_actions()
        
        self.storage.update_macro(self.macro)
        self.macro_saved.emit()
        self.close()
    
    def _delete_macro(self):
        """Удаляет макрос."""
        reply = QMessageBox.question(
            self, "Удаление макроса",
            f"Вы уверены, что хотите удалить макрос '{self.macro.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.delete_macro(self.macro.id)
            self.close()
