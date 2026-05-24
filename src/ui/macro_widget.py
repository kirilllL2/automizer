"""
UI модуль для управления макросами.
Показывает список макросов и позволяет их запускать/останавливать.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

from src.macro import MacroStorage
from src.ui.main_window import ModernStyle


class MacrosWidget(QWidget):
    """Основной виджет управления макросами (вкладка)."""
    
    def __init__(self, storage: MacroStorage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._setup_ui()
        
        # Таймер для обновления статуса выполнения
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(500)  # Обновляем каждые 500мс
    
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
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Таблица макросов
        self.macros_table = QTableWidget()
        self.macros_table.setColumnCount(3)
        self.macros_table.setHorizontalHeaderLabels([
            "Название", "Описание", "Статус"
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
        self.macros_table.itemSelectionChanged.connect(self._on_macro_selected)
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
        
        self.stop_btn = QPushButton("⏹️ Остановить")
        self.stop_btn.setObjectName("dangerBtn")
        self.stop_btn.clicked.connect(self._stop_macro)
        self.stop_btn.setEnabled(False)
        actions_layout.addWidget(self.stop_btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions_card)
        
        # Загружаем макросы
        self._load_macros()
    
    def _load_macros(self):
        """Загружает список макросов."""
        self.storage.reload_macros()
        self.macros_table.setRowCount(0)
        macros = self.storage.list_macros()
        
        for macro in macros:
            row = self.macros_table.rowCount()
            self.macros_table.insertRow(row)
            
            name_item = QTableWidgetItem(macro.name)
            name_item.setData(Qt.ItemDataRole.UserRole, macro.id)
            self.macros_table.setItem(row, 0, name_item)
            
            self.macros_table.setItem(row, 1, QTableWidgetItem(macro.description))
            
            status = "🟢 Выполняется" if macro.is_running else "⚪ Ожидание"
            self.macros_table.setItem(row, 2, QTableWidgetItem(status))
        
        self.macros_table.itemSelectionChanged.connect(self._on_macro_selected)
    
    def _update_status(self):
        """Обновляет статус выполнения макросов."""
        for row in range(self.macros_table.rowCount()):
            item = self.macros_table.item(row, 0)
            if item:
                macro_id = item.data(Qt.ItemDataRole.UserRole)
                macro_info = self.storage.get_macro(macro_id)
                if macro_info:
                    status = "🟢 Выполняется" if macro_info.is_running else "⚪ Ожидание"
                    self.macros_table.setItem(row, 2, QTableWidgetItem(status))
    
    def _on_macro_selected(self):
        """Выбран макрос в таблице."""
        selected = len(self.macros_table.selectedItems()) > 0
        self.run_btn.setEnabled(selected)
        
        # Кнопка остановки активна только если макрос выполняется
        selected_rows = self.macros_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            item = self.macros_table.item(row, 0)
            if item:
                macro_id = item.data(Qt.ItemDataRole.UserRole)
                macro_info = self.storage.get_macro(macro_id)
                self.stop_btn.setEnabled(macro_info and macro_info.is_running)
        else:
            self.stop_btn.setEnabled(False)
    
    def _get_selected_macro_id(self) -> str | None:
        """Получает ID выбранного макроса."""
        selected_rows = self.macros_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        item = self.macros_table.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def _run_macro(self):
        """Запускает выбранный макрос."""
        macro_id = self._get_selected_macro_id()
        if macro_id:
            macro_info = self.storage.get_macro(macro_id)
            if macro_info:
                reply = QMessageBox.question(
                    self, "Запуск макроса",
                    f"Запустить макрос '{macro_info.name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    success = self.storage.execute_macro(macro_id)
                    if success:
                        self._update_status()
                    else:
                        QMessageBox.warning(self, "Ошибка", "Не удалось запустить макрос")
    
    def _stop_macro(self):
        """Останавливает выбранный макрос."""
        macro_id = self._get_selected_macro_id()
        if macro_id:
            macro_info = self.storage.get_macro(macro_id)
            if macro_info and macro_info.is_running:
                reply = QMessageBox.question(
                    self, "Остановка макроса",
                    f"Остановить макрос '{macro_info.name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.storage.stop_macro(macro_id)
                    self._update_status()

