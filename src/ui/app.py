"""
Современный UI модуль для управления нормализацией процессов и скриншотами.
Использует CustomTkinter для современного дизайна с закругленными углами, градиентами и тенями.

Архитектура:
- Боковая навигация с иконками
- Адаптивный layout с использованием grid
- Модальные окна для редактирования координат
- Предпросмотр области с полупрозрачной рамкой
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable
import threading

from src.window_manager import WindowManager, WindowInfo
from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.storage import PresetStorage
from src.screenshot import ScreenshotManager, ScreenshotInfo
from src.screenshot.presets import ScreenshotPresetStorage, ScreenshotPreset


# Цветовая схема - мягкие пастельные тона
COLOR_SCHEME = {
    "bg_primary": "#f8fafc",        # Очень светлый фон
    "bg_secondary": "#ffffff",      # Белый для карточек
    "bg_accent": "#e2e8f0",         # Мягкий акцент
    "text_primary": "#2d3748",      # Темно-серый текст
    "text_secondary": "#718096",    # Светло-серый текст
    "accent": "#667eea",            # Мягкий синий
    "accent_hover": "#5a67d8",      # Темнее при наведении
    "success": "#48bb78",           # Зеленый
    "warning": "#ed8936",           # Оранжевый
    "danger": "#f56565",            # Красный
}

# Настройка темы CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class OverlayPreview(ctk.CTkToplevel):
    """Полупрозрачное окно для предпросмотра области."""
    
    def __init__(self, parent, x: int, y: int, width: int, height: int):
        super().__init__(parent)
        
        self.overrideredirect(True)  # Убрать рамки окна
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.3)  # Полупрозрачность
        
        # Позиционирование
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Фон с цветной рамкой
        self.configure(fg_color=(COLOR_SCHEME["accent"], COLOR_SCHEME["accent_hover"]))
        
        # Рамка внутри для видимости
        border_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=3, border_color="#ffffff")
        border_frame.pack(fill="both", expand=True)


class CoordinateEditorDialog(ctk.CTkToplevel):
    """Модальное окно для редактирования координат с предпросмотром."""
    
    def __init__(self, parent, title: str, x: int = 0, y: int = 0, width: int = 800, height: int = 600,
                 on_confirm: Callable[[int, int, int, int], None] = None):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("500x550")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.x_var = ctk.StringVar(value=str(x))
        self.y_var = ctk.StringVar(value=str(y))
        self.width_var = ctk.StringVar(value=str(width))
        self.height_var = ctk.StringVar(value=str(height))
        self.step_var = ctk.StringVar(value="10")  # Изменяемый шаг
        
        self.on_confirm = on_confirm
        self.preview_window: Optional[OverlayPreview] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame, 
            text="📐 Редактор координат",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLOR_SCHEME["text_primary"]
        )
        title_label.pack(pady=(0, 20))
        
        # Поле шага
        step_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_SCHEME["bg_secondary"])
        step_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(step_frame, text="Шаг (px):", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        self.step_entry = ctk.CTkEntry(step_frame, textvariable=self.step_var, width=80)
        self.step_entry.pack(side="left", padx=10)
        
        # Координаты X, Y
        coord_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_SCHEME["bg_secondary"])
        coord_frame.pack(fill="x", pady=10)
        
        # X
        x_row = ctk.CTkFrame(coord_frame, fg_color="transparent")
        x_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(x_row, text="X:", width=30, font=ctk.CTkFont(size=14)).pack(side="left")
        
        btn_decrement_x = ctk.CTkButton(x_row, text="◀", width=40, command=self._decrement_x)
        btn_decrement_x.pack(side="left", padx=5)
        
        self.x_entry = ctk.CTkEntry(x_row, textvariable=self.x_var, width=80)
        self.x_entry.pack(side="left", padx=5)
        
        btn_increment_x = ctk.CTkButton(x_row, text="▶", width=40, command=self._increment_x)
        btn_increment_x.pack(side="left", padx=5)
        
        # Y
        y_row = ctk.CTkFrame(coord_frame, fg_color="transparent")
        y_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(y_row, text="Y:", width=30, font=ctk.CTkFont(size=14)).pack(side="left")
        
        btn_decrement_y = ctk.CTkButton(y_row, text="▲", width=40, command=self._increment_y)
        btn_decrement_y.pack(side="left", padx=5)
        
        self.y_entry = ctk.CTkEntry(y_row, textvariable=self.y_var, width=80)
        self.y_entry.pack(side="left", padx=5)
        
        btn_increment_y = ctk.CTkButton(y_row, text="▼", width=40, command=self._decrement_y)
        btn_increment_y.pack(side="left", padx=5)
        
        # Размеры Width, Height
        size_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_SCHEME["bg_secondary"])
        size_frame.pack(fill="x", pady=10)
        
        # Width
        w_row = ctk.CTkFrame(size_frame, fg_color="transparent")
        w_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(w_row, text="W:", width=30, font=ctk.CTkFont(size=14)).pack(side="left")
        
        btn_decrement_w = ctk.CTkButton(w_row, text="◀", width=40, command=self._decrement_width)
        btn_decrement_w.pack(side="left", padx=5)
        
        self.width_entry = ctk.CTkEntry(w_row, textvariable=self.width_var, width=80)
        self.width_entry.pack(side="left", padx=5)
        
        btn_increment_w = ctk.CTkButton(w_row, text="▶", width=40, command=self._increment_width)
        btn_increment_w.pack(side="left", padx=5)
        
        # Height
        h_row = ctk.CTkFrame(size_frame, fg_color="transparent")
        h_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(h_row, text="H:", width=30, font=ctk.CTkFont(size=14)).pack(side="left")
        
        btn_decrement_h = ctk.CTkButton(h_row, text="▲", width=40, command=self._increment_height)
        btn_decrement_h.pack(side="left", padx=5)
        
        self.height_entry = ctk.CTkEntry(h_row, textvariable=self.height_var, width=80)
        self.height_entry.pack(side="left", padx=5)
        
        btn_increment_h = ctk.CTkButton(h_row, text="▼", width=40, command=self._decrement_height)
        btn_increment_h.pack(side="left", padx=5)
        
        # Кнопки действий
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        preview_btn = ctk.CTkButton(
            button_frame,
            text="👁️ Предпросмотр",
            command=self._show_preview,
            fg_color=COLOR_SCHEME["warning"],
            hover_color="#dd6b20"
        )
        preview_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="✓ Применить",
            command=self._confirm,
            fg_color=COLOR_SCHEME["success"],
            hover_color="#38a169"
        )
        confirm_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="✕ Отмена",
            command=self.destroy,
            fg_color=COLOR_SCHEME["danger"],
            hover_color="#e53e3e"
        )
        cancel_btn.pack(side="left", padx=5, expand=True, fill="x")
    
    def _get_step(self) -> int:
        try:
            return int(self.step_var.get())
        except ValueError:
            return 10
    
    def _decrement_x(self):
        try:
            val = int(self.x_var.get()) - self._get_step()
            self.x_var.set(str(max(0, val)))
        except ValueError:
            pass
    
    def _increment_x(self):
        try:
            val = int(self.x_var.get()) + self._get_step()
            self.x_var.set(str(val))
        except ValueError:
            pass
    
    def _increment_y(self):
        try:
            val = int(self.y_var.get()) - self._get_step()
            self.y_var.set(str(max(0, val)))
        except ValueError:
            pass
    
    def _decrement_y(self):
        try:
            val = int(self.y_var.get()) + self._get_step()
            self.y_var.set(str(val))
        except ValueError:
            pass
    
    def _decrement_width(self):
        try:
            val = int(self.width_var.get()) - self._get_step()
            self.width_var.set(str(max(100, val)))
        except ValueError:
            pass
    
    def _increment_width(self):
        try:
            val = int(self.width_var.get()) + self._get_step()
            self.width_var.set(str(val))
        except ValueError:
            pass
    
    def _increment_height(self):
        try:
            val = int(self.height_var.get()) - self._get_step()
            self.height_var.set(str(max(100, val)))
        except ValueError:
            pass
    
    def _decrement_height(self):
        try:
            val = int(self.height_var.get()) + self._get_step()
            self.height_var.set(str(val))
        except ValueError:
            pass
    
    def _show_preview(self):
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
        
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            w = int(self.width_var.get())
            h = int(self.height_var.get())
            
            self.preview_window = OverlayPreview(self, x, y, w, h)
            
            # Автозакрытие через 3 секунды
            self.after(3000, self._close_preview)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные значения координат")
    
    def _close_preview(self):
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
    
    def _confirm(self):
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            w = int(self.width_var.get())
            h = int(self.height_var.get())
            
            if self.on_confirm:
                self.on_confirm(x, y, w, h)
            
            self.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные значения координат")
    
    def destroy(self):
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
        super().destroy()


class ProcessCard(ctk.CTkFrame):
    """Карточка процесса в списке."""
    
    def __init__(self, parent, window_info: WindowInfo, on_select: Callable[[WindowInfo], None]):
        super().__init__(parent, fg_color=COLOR_SCHEME["bg_secondary"], corner_radius=15)
        
        self.window_info = window_info
        self.on_select = on_select
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.configure(border_width=1, border_color=COLOR_SCHEME["bg_accent"])
        
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=15, pady=12)
        
        # Иконка и название
        info_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        icon_label = ctk.CTkLabel(
            info_frame, 
            text="🖥️",
            font=ctk.CTkFont(size=24)
        )
        icon_label.pack(side="left", padx=(0, 12))
        
        text_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            text_frame,
            text=self.window_info.title[:50] + ("..." if len(self.window_info.title) > 50 else ""),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x")
        
        details_label = ctk.CTkLabel(
            text_frame,
            text=f"PID: {self.window_info.window_id} | {self.window_info.width}x{self.window.height} @ ({self.window_info.x}, {self.window_info.y})",
            font=ctk.CTkFont(size=11),
            text_color=COLOR_SCHEME["text_secondary"],
            anchor="w"
        )
        details_label.pack(fill="x", pady=(4, 0))
        
        # Кнопка выбора
        select_btn = ctk.CTkButton(
            main_layout,
            text="Выбрать",
            width=100,
            corner_radius=20,
            fg_color=COLOR_SCHEME["accent"],
            hover_color=COLOR_SCHEME["accent_hover"],
            command=lambda: self.on_select(self.window_info)
        )
        select_btn.pack(side="right", padx=(10, 0))


class PresetCard(ctk.CTkFrame):
    """Карточка пресета."""
    
    def __init__(self, parent, preset: NormalizationPreset, on_edit: Callable, on_delete: Callable, on_apply: Callable):
        super().__init__(parent, fg_color=COLOR_SCHEME["bg_secondary"], corner_radius=15)
        
        self.preset = preset
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_apply = on_apply
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.configure(border_width=1, border_color=COLOR_SCHEME["bg_accent"])
        
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=15, pady=12)
        
        # Иконка и название
        info_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        icon_label = ctk.CTkLabel(
            info_frame, 
            text="⚡",
            font=ctk.CTkFont(size=24)
        )
        icon_label.pack(side="left", padx=(0, 12))
        
        text_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            text_frame,
            text=self.preset.name,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x")
        
        details_label = ctk.CTkLabel(
            text_frame,
            text=f"{self.preset.x}, {self.preset.y}, {self.preset.width}x{self.preset.height}",
            font=ctk.CTkFont(size=11),
            text_color=COLOR_SCHEME["text_secondary"],
            anchor="w"
        )
        details_label.pack(fill="x", pady=(4, 0))
        
        # Кнопки действий
        btn_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
        btn_frame.pack(side="right")
        
        apply_btn = ctk.CTkButton(
            btn_frame,
            text="✓",
            width=40,
            corner_radius=20,
            fg_color=COLOR_SCHEME["success"],
            hover_color="#38a169",
            command=self.on_apply
        )
        apply_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✎",
            width=40,
            corner_radius=20,
            fg_color=COLOR_SCHEME["warning"],
            hover_color="#dd6b20",
            command=self.on_edit
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑",
            width=40,
            corner_radius=20,
            fg_color=COLOR_SCHEME["danger"],
            hover_color="#e53e3e",
            command=self.on_delete
        )
        delete_btn.pack(side="left", padx=5)


class MainWindow(ctk.CTk):
    """Главное окно приложения с боковой навигацией."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Process Normalizer")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Инициализация менеджеров
        self.window_manager = WindowManager()
        self.normalizer = ProcessNormalizer()
        self.preset_storage = PresetStorage()
        self.screenshot_manager = ScreenshotManager()
        self.screenshot_preset_storage = ScreenshotPresetStorage()
        
        self.current_window: Optional[WindowInfo] = None
        
        self._setup_ui()
        self._load_processes()
    
    def _setup_ui(self):
        # Основной layout с grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Боковая панель
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Логотип
        logo_label = ctk.CTkLabel(
            sidebar,
            text="🎯 Process\nNormalizer",
            font=ctk.CTkFont(size=18, weight="bold"),
            justify="center"
        )
        logo_label.pack(pady=30)
        
        # Навигационные кнопки
        nav_buttons = [
            ("🏠 Главная", self._show_home),
            ("🎯 Процессы", self._show_processes),
            ("⚡ Пресеты", self._show_presets),
            ("📸 Скриншоты", self._show_screenshots),
            ("⚙️ Настройки", self._show_settings),
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                height=50,
                corner_radius=10,
                fg_color="transparent",
                hover_color=COLOR_SCHEME["bg_accent"],
                anchor="w",
                padx=20,
                command=command
            )
            btn.pack(fill="x", padx=10, pady=5)
        
        # Основная область контента
        self.content_frame = ctk.CTkFrame(self, fg_color=COLOR_SCHEME["bg_primary"], corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Контейнеры для разных вкладок
        self.home_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.processes_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.presets_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.screenshots_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.settings_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        self._setup_home_tab()
        self._setup_processes_tab()
        self._setup_presets_tab()
        self._setup_screenshots_tab()
        self._setup_settings_tab()
        
        # Показать главную по умолчанию
        self._show_home()
    
    def _clear_content(self):
        for container in [self.home_container, self.processes_container, 
                          self.presets_container, self.screenshots_container, 
                          self.settings_container]:
            container.grid_forget()
    
    def _show_home(self):
        self._clear_content()
        self.home_container.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
    
    def _show_processes(self):
        self._clear_content()
        self.processes_container.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        self._load_processes()
    
    def _show_presets(self):
        self._clear_content()
        self.presets_container.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        self._load_presets()
    
    def _show_screenshots(self):
        self._clear_content()
        self.screenshots_container.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        self._load_screenshots()
    
    def _show_settings(self):
        self._clear_content()
        self.settings_container.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
    
    def _setup_home_tab(self):
        # Заголовок
        header = ctk.CTkLabel(
            self.home_container,
            text="Добро пожаловать!",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_SCHEME["text_primary"]
        )
        header.pack(pady=(0, 10))
        
        subtitle = ctk.CTkLabel(
            self.home_container,
            text="Управляйте окнами процессов и создавайте пресеты",
            font=ctk.CTkFont(size=16),
            text_color=COLOR_SCHEME["text_secondary"]
        )
        subtitle.pack(pady=(0, 30))
        
        # Статус
        status_frame = ctk.CTkFrame(self.home_container, fg_color=COLOR_SCHEME["bg_secondary"], corner_radius=15)
        status_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            status_frame,
            text="📊 Статистика",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        stats_grid = ctk.CTkFrame(status_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=10)
        
        presets_count = len(self.preset_storage.get_all_presets())
        screenshots_count = len(self.screenshot_preset_storage.get_all_presets())
        
        stat_items = [
            ("🎯 Пресетов", str(presets_count)),
            ("📸 Скриншотов", str(screenshots_count)),
            ("🖥️ Процессов", "Активно"),
        ]
        
        for i, (label, value) in enumerate(stat_items):
            stat_box = ctk.CTkFrame(stats_grid, fg_color=COLOR_SCHEME["bg_accent"], corner_radius=10)
            stat_box.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            stats_grid.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                stat_box,
                text=value,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=COLOR_SCHEME["accent"]
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                stat_box,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=COLOR_SCHEME["text_secondary"]
            ).pack(pady=(0, 15))
    
    def _setup_processes_tab(self):
        # Заголовок
        header_frame = ctk.CTkFrame(self.processes_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="🎯 Выбор процесса",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="⟳ Обновить",
            command=self._load_processes,
            width=120,
            corner_radius=20
        )
        refresh_btn.pack(side="right")
        
        # Поиск
        search_frame = ctk.CTkFrame(self.processes_container, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 20))
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_processes())
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Поиск по названию окна...",
            textvariable=self.search_var,
            height=45,
            corner_radius=20
        )
        search_entry.pack(fill="x")
        
        # Список процессов
        self.processes_list_frame = ctk.CTkFrame(self.processes_container, fg_color="transparent")
        self.processes_list_frame.pack(fill="both", expand=True)
    
    def _load_processes(self):
        # Очистка списка
        for widget in self.processes_list_frame.winfo_children():
            widget.destroy()
        
        windows = self.window_manager.get_windows()
        
        if not windows:
            ctk.CTkLabel(
                self.processes_list_frame,
                text="Нет активных окон",
                font=ctk.CTkFont(size=16),
                text_color=COLOR_SCHEME["text_secondary"]
            ).pack(pady=50)
            return
        
        # Создание карточек
        for window in windows:
            card = ProcessCard(
                self.processes_list_frame,
                window,
                on_select=self._on_process_selected
            )
            card.pack(fill="x", pady=8, padx=5)
    
    def _filter_processes(self):
        query = self.search_var.get().lower()
        
        for widget in self.processes_list_frame.winfo_children():
            if isinstance(widget, ProcessCard):
                if query and query not in widget.window_info.title.lower():
                    widget.pack_forget()
                else:
                    widget.pack(fill="x", pady=8, padx=5)
    
    def _on_process_selected(self, window: WindowInfo):
        self.current_window = window
        
        # Открыть редактор координат
        dialog = CoordinateEditorDialog(
            self,
            title="📐 Настройка позиции и размера",
            x=window.x,
            y=window.y,
            width=window.width,
            height=window.height,
            on_confirm=lambda x, y, w, h: self._apply_position(window, x, y, w, h)
        )
    
    def _apply_position(self, window: WindowInfo, x: int, y: int, width: int, height: int):
        try:
            self.normalizer.normalize_window(
                window.window_id,
                x=x,
                y=y,
                width=width,
                height=height
            )
            messagebox.showinfo("Успех", f"Окно '{window.title}' обновлено!")
            self._load_processes()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить окно: {e}")
    
    def _setup_presets_tab(self):
        # Заголовок
        header_frame = ctk.CTkFrame(self.presets_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="⚡ Пресеты процессов",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Добавить пресет",
            command=self._add_preset,
            corner_radius=20
        )
        add_btn.pack(side="right")
        
        # Список пресетов
        self.presets_list_frame = ctk.CTkFrame(self.presets_container, fg_color="transparent")
        self.presets_list_frame.pack(fill="both", expand=True)
    
    def _load_presets(self):
        # Очистка списка
        for widget in self.presets_list_frame.winfo_children():
            widget.destroy()
        
        presets = self.preset_storage.get_all_presets()
        
        if not presets:
            ctk.CTkLabel(
                self.presets_list_frame,
                text="Нет сохраненных пресетов",
                font=ctk.CTkFont(size=16),
                text_color=COLOR_SCHEME["text_secondary"]
            ).pack(pady=50)
            return
        
        # Создание карточек
        for preset in presets:
            card = PresetCard(
                self.presets_list_frame,
                preset,
                on_edit=lambda p=preset: self._edit_preset(p),
                on_delete=lambda p=preset: self._delete_preset(p),
                on_apply=lambda p=preset: self._apply_preset(p)
            )
            card.pack(fill="x", pady=8, padx=5)
    
    def _add_preset(self):
        dialog = CoordinateEditorDialog(
            self,
            title="➕ Новый пресет",
            on_confirm=self._save_preset
        )
    
    def _save_preset(self, x: int, y: int, width: int, height: int):
        name_dialog = ctk.CTkInputDialog(
            text="Введите название пресета:",
            title="Сохранение пресета"
        )
        name = name_dialog.get_input()
        
        if name:
            preset = NormalizationPreset(
                name=name,
                x=x,
                y=y,
                width=width,
                height=height
            )
            self.preset_storage.save_preset(preset)
            self._load_presets()
            messagebox.showinfo("Успех", "Пресет сохранен!")
    
    def _edit_preset(self, preset: NormalizationPreset):
        dialog = CoordinateEditorDialog(
            self,
            title=f"✏️ Редактирование: {preset.name}",
            x=preset.x,
            y=preset.y,
            width=preset.width,
            height=preset.height,
            on_confirm=lambda x, y, w, h: self._update_preset(preset, x, y, w, h)
        )
    
    def _update_preset(self, preset: NormalizationPreset, x: int, y: int, width: int, height: int):
        preset.x = x
        preset.y = y
        preset.width = width
        preset.height = height
        self.preset_storage.save_preset(preset)
        self._load_presets()
        messagebox.showinfo("Успех", "Пресет обновлен!")
    
    def _delete_preset(self, preset: NormalizationPreset):
        if messagebox.askyesno("Подтверждение", f"Удалить пресет '{preset.name}'?"):
            self.preset_storage.delete_preset(preset.id)
            self._load_presets()
    
    def _apply_preset(self, preset: NormalizationPreset):
        if not self.current_window:
            messagebox.showwarning("Внимание", "Сначала выберите процесс на вкладке 'Процессы'")
            return
        
        try:
            self.normalizer.normalize_window(
                self.current_window.window_id,
                x=preset.x,
                y=preset.y,
                width=preset.width,
                height=preset.height
            )
            messagebox.showinfo("Успех", f"Пресет '{preset.name}' применен к '{self.current_window.title}'")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить пресет: {e}")
    
    def _setup_screenshots_tab(self):
        # Заголовок
        header_frame = ctk.CTkFrame(self.screenshots_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="📸 Пресеты скриншотов",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Добавить область",
            command=self._add_screenshot_preset,
            corner_radius=20
        )
        add_btn.pack(side="right")
        
        # Список пресетов скриншотов
        self.screenshots_list_frame = ctk.CTkFrame(self.screenshots_container, fg_color="transparent")
        self.screenshots_list_frame.pack(fill="both", expand=True)
    
    def _load_screenshots(self):
        # Очистка списка
        for widget in self.screenshots_list_frame.winfo_children():
            widget.destroy()
        
        presets = self.screenshot_preset_storage.get_all_presets()
        
        if not presets:
            ctk.CTkLabel(
                self.screenshots_list_frame,
                text="Нет сохраненных областей для скриншотов",
                font=ctk.CTkFont(size=16),
                text_color=COLOR_SCHEME["text_secondary"]
            ).pack(pady=50)
            return
        
        # Создание карточек
        for preset in presets:
            card = ctk.CTkFrame(
                self.screenshots_list_frame,
                fg_color=COLOR_SCHEME["bg_secondary"],
                corner_radius=15
            )
            card.configure(border_width=1, border_color=COLOR_SCHEME["bg_accent"])
            card.pack(fill="x", pady=8, padx=5)
            
            main_layout = ctk.CTkFrame(card, fg_color="transparent")
            main_layout.pack(fill="both", expand=True, padx=15, pady=12)
            
            # Информация
            info_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True)
            
            ctk.CTkLabel(info_frame, text="📸", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 12))
            
            text_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)
            
            ctk.CTkLabel(
                text_frame,
                text=preset.name,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(fill="x")
            
            ctk.CTkLabel(
                text_frame,
                text=f"{preset.x}, {preset.y}, {preset.width}x{preset.height}",
                font=ctk.CTkFont(size=11),
                text_color=COLOR_SCHEME["text_secondary"]
            ).pack(fill="x", pady=(4, 0))
            
            # Кнопки
            btn_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
            btn_frame.pack(side="right")
            
            ctk.CTkButton(
                btn_frame,
                text="📷",
                width=40,
                corner_radius=20,
                fg_color=COLOR_SCHEME["accent"],
                hover_color=COLOR_SCHEME["accent_hover"],
                command=lambda p=preset: self._take_screenshot(p)
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                btn_frame,
                text="✎",
                width=40,
                corner_radius=20,
                fg_color=COLOR_SCHEME["warning"],
                hover_color="#dd6b20",
                command=lambda p=preset: self._edit_screenshot_preset(p)
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                btn_frame,
                text="🗑",
                width=40,
                corner_radius=20,
                fg_color=COLOR_SCHEME["danger"],
                hover_color="#e53e3e",
                command=lambda p=preset: self._delete_screenshot_preset(p)
            ).pack(side="left", padx=5)
    
    def _add_screenshot_preset(self):
        dialog = CoordinateEditorDialog(
            self,
            title="📸 Новая область для скриншота",
            on_confirm=self._save_screenshot_preset
        )
    
    def _save_screenshot_preset(self, x: int, y: int, width: int, height: int):
        name_dialog = ctk.CTkInputDialog(
            text="Введите название области:",
            title="Сохранение области"
        )
        name = name_dialog.get_input()
        
        if name:
            preset = ScreenshotPreset(
                name=name,
                x=x,
                y=y,
                width=width,
                height=height
            )
            self.screenshot_preset_storage.save_preset(preset)
            self._load_screenshots()
            messagebox.showinfo("Успех", "Область сохранена!")
    
    def _edit_screenshot_preset(self, preset: ScreenshotPreset):
        dialog = CoordinateEditorDialog(
            self,
            title=f"✏️ Редактирование: {preset.name}",
            x=preset.x,
            y=preset.y,
            width=preset.width,
            height=preset.height,
            on_confirm=lambda x, y, w, h: self._update_screenshot_preset(preset, x, y, w, h)
        )
    
    def _update_screenshot_preset(self, preset: ScreenshotPreset, x: int, y: int, width: int, height: int):
        preset.x = x
        preset.y = y
        preset.width = width
        preset.height = height
        self.screenshot_preset_storage.save_preset(preset)
        self._load_screenshots()
        messagebox.showinfo("Успех", "Область обновлена!")
    
    def _delete_screenshot_preset(self, preset: ScreenshotPreset):
        if messagebox.askyesno("Подтверждение", f"Удалить область '{preset.name}'?"):
            self.screenshot_preset_storage.delete_preset(preset.id)
            self._load_screenshots()
    
    def _take_screenshot(self, preset: ScreenshotPreset):
        try:
            screenshot = self.screenshot_manager.capture_region(
                x=preset.x,
                y=preset.y,
                width=preset.width,
                height=preset.height
            )
            
            filename = f"screenshot_{preset.name}_{screenshot.timestamp}.png"
            screenshot.save(filename)
            
            messagebox.showinfo("Успех", f"Скриншот сохранен: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сделать скриншот: {e}")
    
    def _setup_settings_tab(self):
        ctk.CTkLabel(
            self.settings_container,
            text="⚙️ Настройки",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=30)
        
        settings_frame = ctk.CTkFrame(self.settings_container, fg_color=COLOR_SCHEME["bg_secondary"], corner_radius=15)
        settings_frame.pack(fill="x", padx=50, pady=20)
        
        ctk.CTkLabel(
            settings_frame,
            text="Настройки будут добавлены в будущих версиях",
            font=ctk.CTkFont(size=16),
            text_color=COLOR_SCHEME["text_secondary"]
        ).pack(pady=40)


def run_app():
    """Запуск приложения."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    run_app()
