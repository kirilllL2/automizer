"""
UI модуль для управления нормализацией процессов и скриншотами.

Предоставляет Tkinter интерфейс с вкладками:
- Вкладка 1: Выбор процесса из списка с поиском и настройка позиции/размера
- Вкладка 2: Применение пресетов и управление ими
- Вкладка 3: Работа со скриншотами (выделение области, создание, привязка к пресету)

Также поддерживает:
- Сохранение текущих параметров как пресет
- Редактирование и удаление пресетов
- Создание скриншотов с выделением области
- Привязка скриншотов к пресетам процессов
- Стильный современный дизайн
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from typing import Optional, Callable

from src.window_manager import WindowManager, WindowInfo
from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.storage import PresetStorage
from src.screenshot import ScreenshotManager, ScreenshotInfo


# Стили приложения
STYLE_COLORS = {
    "bg_primary": "#2b2d42",
    "bg_secondary": "#3d405b",
    "bg_accent": "#5e6472",
    "fg_primary": "#edf2f4",
    "fg_secondary": "#a8b2c1",
    "accent": "#00adb5",
    "accent_hover": "#00d4dc",
    "success": "#4caf50",
    "warning": "#ff9800",
    "danger": "#f44336",
}


def apply_modern_style(widget: tk.Widget) -> None:
    """Применяет современный стиль к виджету."""
    style = ttk.Style()
    
    # Настройка темы
    style.theme_use('clam')
    
    # TFrame
    style.configure(
        "TFrame",
        background=STYLE_COLORS["bg_secondary"]
    )
    
    # TLabel
    style.configure(
        "TLabel",
        background=STYLE_COLORS["bg_secondary"],
        foreground=STYLE_COLORS["fg_primary"],
        font=("Segoe UI", 10)
    )
    
    # TLabelFrame
    style.configure(
        "TLabelframe",
        background=STYLE_COLORS["bg_secondary"],
        foreground=STYLE_COLORS["accent"],
        bordercolor=STYLE_COLORS["bg_accent"],
        lightcolor=STYLE_COLORS["bg_accent"],
        darkcolor=STYLE_COLORS["bg_accent"],
    )
    style.configure(
        "TLabelframe.Label",
        background=STYLE_COLORS["bg_secondary"],
        foreground=STYLE_COLORS["accent"],
        font=("Segoe UI", 11, "bold")
    )
    
    # TButton
    style.configure(
        "TButton",
        background=STYLE_COLORS["accent"],
        foreground=STYLE_COLORS["fg_primary"],
        bordercolor=STYLE_COLORS["accent"],
        focuscolor=STYLE_COLORS["accent_hover"],
        padding=(15, 8),
        font=("Segoe UI", 10, "bold")
    )
    style.map(
        "TButton",
        background=[("active", STYLE_COLORS["accent_hover"])],
        foreground=[("active", STYLE_COLORS["fg_primary"])],
    )
    
    # TEntry
    style.configure(
        "TEntry",
        fieldbackground="#1a1c29",
        foreground=STYLE_COLORS["fg_primary"],
        bordercolor=STYLE_COLORS["bg_accent"],
        lightcolor=STYLE_COLORS["bg_accent"],
        darkcolor=STYLE_COLORS["bg_accent"],
        padding=8,
        insertcolor=STYLE_COLORS["fg_primary"],
    )
    
    # Treeview
    style.configure(
        "Treeview",
        background="#1a1c29",
        foreground=STYLE_COLORS["fg_primary"],
        fieldbackground="#1a1c29",
        rowheight=28,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background=STYLE_COLORS["bg_accent"],
        foreground=STYLE_COLORS["fg_primary"],
        font=("Segoe UI", 10, "bold"),
        padding=8,
    )
    style.map(
        "Treeview",
        background=[("selected", STYLE_COLORS["accent"])],
        foreground=[("selected", STYLE_COLORS["fg_primary"])],
    )
    
    # Notebook (вкладки)
    style.configure(
        "TNotebook",
        background=STYLE_COLORS["bg_secondary"],
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        background=STYLE_COLORS["bg_accent"],
        foreground=STYLE_COLORS["fg_secondary"],
        padding=(20, 10),
        font=("Segoe UI", 11, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", STYLE_COLORS["accent"])],
        foreground=[("selected", STYLE_COLORS["fg_primary"])],
    )


class ProcessSelectorFrame(ttk.LabelFrame):
    """Фрейм для выбора процесса с поиском."""

    def __init__(self, parent, on_select: Callable[[WindowInfo], None]):
        super().__init__(parent, text="📋 Выберите процесс")
        self.on_select = on_select
        self._windows: list[WindowInfo] = []
        self._selected_window: Optional[WindowInfo] = None

        self._setup_ui()
        self._refresh_windows()

    def _setup_ui(self) -> None:
        # Поисковая строка
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)

        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.insert(0, "🔍 Поиск по названию окна...")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)

        refresh_btn = ttk.Button(search_frame, text="⟳ Обновить", command=self._refresh_windows)
        refresh_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Список окон
        columns = ("title", "position", "size")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        self.tree.heading("title", text="Заголовок окна")
        self.tree.heading("position", text="Позиция")
        self.tree.heading("size", text="Размер")

        self.tree.column("title", width=350, minwidth=200)
        self.tree.column("position", width=130, minwidth=100)
        self.tree.column("size", width=110, minwidth=80)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _on_search_focus_in(self, event):
        if self.search_var.get().startswith("🔍"):
            self.search_var.set("")

    def _on_search_focus_out(self, event):
        if not self.search_var.get():
            self.search_var.set("🔍 Поиск по названию окна...")

    def _on_search_changed(self, *args):
        query = self.search_var.get()
        if query.startswith("🔍"):
            query = ""
        self._filter_windows(query)

    def _refresh_windows(self) -> None:
        wm = WindowManager()
        self._windows = wm.get_windows()
        self._filter_windows(self.search_var.get() if not self.search_var.get().startswith("🔍") else "")

    def _filter_windows(self, query: str) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_term = query.lower()
        filtered = [
            w for w in self._windows
            if not search_term or search_term in w.title.lower()
        ]

        for window in filtered:
            self.tree.insert("", tk.END, iid=str(window.window_id), values=(
                window.title[:50] + "..." if len(window.title) > 50 else window.title,
                f"({window.x}, {window.y})",
                f"{window.width}x{window.height}",
            ))

    def _on_select(self, event) -> None:
        selection = self.tree.selection()
        if selection:
            window_id = int(selection[0])
            for window in self._windows:
                if window.window_id == window_id:
                    self._selected_window = window
                    self.on_select(window)
                    break

    def get_selected_window(self) -> Optional[WindowInfo]:
        return self._selected_window


class PositionSizeFrame(ttk.LabelFrame):
    """Фрейм для указания положения и размеров."""

    def __init__(self, parent):
        super().__init__(parent, text="📐 Положение и размер")
        self._setup_ui()

    def _setup_ui(self) -> None:
        # Координаты
        coord_frame = ttk.Frame(self)
        coord_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(coord_frame, text="X:").grid(row=0, column=0, padx=(0, 5), sticky=tk.E)
        self.x_var = tk.StringVar(value="0")
        self.x_entry = ttk.Entry(coord_frame, textvariable=self.x_var, width=10)
        self.x_entry.grid(row=0, column=1, padx=(0, 15), sticky=tk.W)

        ttk.Label(coord_frame, text="Y:").grid(row=0, column=2, padx=(0, 5), sticky=tk.E)
        self.y_var = tk.StringVar(value="0")
        self.y_entry = ttk.Entry(coord_frame, textvariable=self.y_var, width=10)
        self.y_entry.grid(row=0, column=3, padx=(0, 15), sticky=tk.W)

        # Размеры
        size_frame = ttk.Frame(self)
        size_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(size_frame, text="Ширина:").grid(row=0, column=0, padx=(0, 5), sticky=tk.E)
        self.width_var = tk.StringVar(value="800")
        self.width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=10)
        self.width_entry.grid(row=0, column=1, padx=(0, 15), sticky=tk.W)

        ttk.Label(size_frame, text="Высота:").grid(row=0, column=2, padx=(0, 5), sticky=tk.E)
        self.height_var = tk.StringVar(value="600")
        self.height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=10)
        self.height_entry.grid(row=0, column=3, padx=(0, 15), sticky=tk.W)

        # Кнопки предустановок
        preset_frame = ttk.Frame(self)
        preset_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(preset_frame, text="½ экрана ←", command=self._set_half_left).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="½ экрана →", command=self._set_half_right).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="¼ ↖", command=self._set_quarter_top_left).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="¼ ↗", command=self._set_quarter_top_right).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="¼ ↙", command=self._set_quarter_bottom_left).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="¼ ↘", command=self._set_quarter_bottom_right).pack(side=tk.LEFT, padx=3, pady=3)

    def _get_screen_size(self) -> tuple[int, int]:
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        return screen_width, screen_height

    def _set_half_left(self) -> None:
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h))

    def _set_half_right(self) -> None:
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set(str(screen_w // 2))
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h))

    def _set_quarter_top_left(self) -> None:
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))

    def _set_quarter_top_right(self) -> None:
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set(str(screen_w // 2))
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))

    def _set_quarter_bottom_left(self) -> None:
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set("0")
        self.y_var.set(str(screen_h // 2))
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))

    def _set_quarter_bottom_right(self) -> None:
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set(str(screen_w // 2))
        self.y_var.set(str(screen_h // 2))
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))

    def get_values(self) -> tuple[int, int, int, int]:
        return (
            int(self.x_var.get()),
            int(self.y_var.get()),
            int(self.width_var.get()),
            int(self.height_var.get()),
        )

    def set_from_window(self, window: WindowInfo) -> None:
        self.x_var.set(str(window.x))
        self.y_var.set(str(window.y))
        self.width_var.set(str(window.width))
        self.height_var.set(str(window.height))


class ScreenshotAreaSelector(tk.Toplevel):
    """Диалог для выделения области экрана для скриншота."""

    def __init__(self, parent, on_confirm: Callable[[tuple[int, int, int, int]], None]):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self.result: Optional[tuple[int, int, int, int]] = None
        
        self.title("📸 Выделение области для скриншота")
        self.geometry("800x600")
        
        self.transient(parent)
        self.grab_set()
        
        # Получаем размеры экрана
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Инструкция
        ttk.Label(
            main_frame, 
            text="Выделите область для скриншота:",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(0, 10))
        
        # Поля для координат и размеров
        coord_frame = ttk.LabelFrame(main_frame, text="📐 Параметры области")
        coord_frame.pack(fill=tk.X, pady=10)
        
        # X, Y
        xy_frame = ttk.Frame(coord_frame)
        xy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(xy_frame, text="X:").grid(row=0, column=0, padx=(0, 5), sticky=tk.E)
        self.x_var = tk.StringVar(value="0")
        self.x_entry = ttk.Entry(xy_frame, textvariable=self.x_var, width=10)
        self.x_entry.grid(row=0, column=1, padx=(0, 20), sticky=tk.W)
        
        ttk.Label(xy_frame, text="Y:").grid(row=0, column=2, padx=(0, 5), sticky=tk.E)
        self.y_var = tk.StringVar(value="0")
        self.y_entry = ttk.Entry(xy_frame, textvariable=self.y_var, width=10)
        self.y_entry.grid(row=0, column=3, sticky=tk.W)
        
        # Width, Height
        wh_frame = ttk.Frame(coord_frame)
        wh_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(wh_frame, text="Ширина:").grid(row=0, column=0, padx=(0, 5), sticky=tk.E)
        self.width_var = tk.StringVar(value="800")
        self.width_entry = ttk.Entry(wh_frame, textvariable=self.width_var, width=10)
        self.width_entry.grid(row=0, column=1, padx=(0, 20), sticky=tk.W)
        
        ttk.Label(wh_frame, text="Высота:").grid(row=0, column=2, padx=(0, 5), sticky=tk.E)
        self.height_var = tk.StringVar(value="600")
        self.height_entry = ttk.Entry(wh_frame, textvariable=self.height_var, width=10)
        self.height_entry.grid(row=0, column=3, sticky=tk.W)
        
        # Кнопки предустановок
        preset_frame = ttk.Frame(coord_frame)
        preset_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(preset_frame, text="½ экрана ←", command=self._set_half_left).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="½ экрана →", command=self._set_half_right).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="¼ ↖", command=self._set_quarter_top_left).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="¼ ↗", command=self._set_quarter_top_right).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="¼ ↙", command=self._set_quarter_bottom_left).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="¼ ↘", command=self._set_quarter_bottom_right).pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(preset_frame, text="Полный экран", command=self._set_fullscreen).pack(side=tk.LEFT, padx=3, pady=3)
        
        # Canvas для предпросмотра
        preview_frame = ttk.LabelFrame(main_frame, text="👁️ Предпросмотр")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.canvas = tk.Canvas(preview_frame, bg="#1a1c29", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Привязка событий к canvas
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        
        # Переменные для рисования
        self._rect_id = None
        self._start_x = 0
        self._start_y = 0
        self._scale_x = 1.0
        self._scale_y = 1.0
        
        # Кнопки действий
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="✅ Подтвердить область", command=self._confirm).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ Отмена", command=self._cancel).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="🔍 Показать превью", command=self._show_preview).pack(side=tk.RIGHT, padx=10)
        
        # Обновляем предпросмотр при изменении значений
        self.x_var.trace_add("write", self._update_preview)
        self.y_var.trace_add("write", self._update_preview)
        self.width_var.trace_add("write", self._update_preview)
        self.height_var.trace_add("write", self._update_preview)
        
    def _get_scaled_coords(self, x: int, y: int, w: int, h: int) -> tuple[float, float, float, float]:
        """Преобразует реальные координаты в координаты canvas с учетом масштаба."""
        return (
            x * self._scale_x,
            y * self._scale_y,
            (x + w) * self._scale_x,
            (y + h) * self._scale_y
        )
        
    def _on_canvas_resize(self, event) -> None:
        """Обновляет масштаб при изменении размера canvas."""
        if self.screen_width > 0 and event.width > 0:
            self._scale_x = event.width / self.screen_width
        if self.screen_height > 0 and event.height > 0:
            self._scale_y = event.height / self.screen_height
        self._update_preview()
        
    def _on_mouse_press(self, event) -> None:
        """Начало выделения области."""
        self._start_x = event.x
        self._start_y = event.y
        
    def _on_mouse_drag(self, event) -> None:
        """Перетаскивание для выделения области."""
        if self._rect_id:
            self.canvas.delete(self._rect_id)
        
        # Преобразуем координаты canvas в реальные координаты экрана
        x1 = min(self._start_x, event.x) / self._scale_x
        y1 = min(self._start_y, event.y) / self._scale_y
        x2 = max(self._start_x, event.x) / self._scale_x
        y2 = max(self._start_y, event.y) / self._scale_y
        
        # Обновляем поля ввода
        self.x_var.set(str(int(x1)))
        self.y_var.set(str(int(y1)))
        self.width_var.set(str(int(x2 - x1)))
        self.height_var.set(str(int(y2 - y1)))
        
    def _on_mouse_release(self, event) -> None:
        """Завершение выделения области."""
        pass
        
    def _set_half_left(self) -> None:
        screen_w, screen_h = self.screen_width, self.screen_height
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h))
        
    def _set_half_right(self) -> None:
        screen_w, screen_h = self.screen_width, self.screen_height
        self.x_var.set(str(screen_w // 2))
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h))
        
    def _set_quarter_top_left(self) -> None:
        screen_w, screen_h = self.screen_width, self.screen_height
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))
        
    def _set_quarter_top_right(self) -> None:
        screen_w, screen_h = self.screen_width, self.screen_height
        self.x_var.set(str(screen_w // 2))
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))
        
    def _set_quarter_bottom_left(self) -> None:
        screen_w, screen_h = self.screen_width, self.screen_height
        self.x_var.set("0")
        self.y_var.set(str(screen_h // 2))
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))
        
    def _set_quarter_bottom_right(self) -> None:
        screen_w, screen_h = self.screen_width, self.screen_height
        self.x_var.set(str(screen_w // 2))
        self.y_var.set(str(screen_h // 2))
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))
        
    def _set_fullscreen(self) -> None:
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(self.screen_width))
        self.height_var.set(str(self.screen_height))
        
    def _update_preview(self, *args) -> None:
        """Обновляет предпросмотр выделенной области на canvas."""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            w = int(self.width_var.get())
            h = int(self.height_var.get())
            
            # Ограничиваем значения размерами экрана
            x = max(0, min(x, self.screen_width - 1))
            y = max(0, min(y, self.screen_height - 1))
            w = max(1, min(w, self.screen_width - x))
            h = max(1, min(h, self.screen_height - y))
            
            # Очищаем canvas
            self.canvas.delete("all")
            
            # Рисуем сетку (схематичное изображение экрана)
            grid_color = "#3d405b"
            for i in range(0, int(self.canvas.winfo_width()), 50):
                self.canvas.create_line(i, 0, i, self.canvas.winfo_height(), fill=grid_color, dash=(2, 2))
            for i in range(0, int(self.canvas.winfo_height()), 50):
                self.canvas.create_line(0, i, self.canvas.winfo_width(), i, fill=grid_color, dash=(2, 2))
            
            # Рисуем выделенную область
            x1, y1, x2, y2 = self._get_scaled_coords(x, y, w, h)
            self._rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="#00adb5",
                width=2,
                fill="#00adb5",
                stipple="gray50"
            )
            
            # Добавляем метку с размерами
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2
            self.canvas.create_text(
                label_x, label_y,
                text=f"{w}x{h}",
                fill="#edf2f4",
                font=("Segoe UI", 12, "bold")
            )
            
        except ValueError:
            pass
            
    def _show_preview(self) -> None:
        """Показывает реальное превью области на экране."""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            w = int(self.width_var.get())
            h = int(self.height_var.get())
            
            # Создаем временное окно для превью
            preview = tk.Toplevel(self)
            preview.title("Предпросмотр")
            preview.geometry(f"{w}x{h}+{x}+{y}")
            preview.attributes("-topmost", True)
            preview.configure(bg="red")
            preview.overrideredirect(True)
            preview.wm_attributes("-alpha", 0.3)
            
            # Закрываем через 1 секунду
            preview.after(1000, preview.destroy)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные значения: {e}")
            
    def _confirm(self) -> None:
        """Подтверждает выбранную область."""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            w = int(self.width_var.get())
            h = int(self.height_var.get())
            
            if w <= 0 or h <= 0:
                messagebox.showwarning("Предупреждение", "Размеры области должны быть положительными")
                return
                
            self.result = (x, y, w, h)
            self.on_confirm(self.result)
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные значения: {e}")
            
    def _cancel(self) -> None:
        """Отменяет выбор области."""
        self.destroy()


class ScreenshotManagerFrame(ttk.LabelFrame):
    """Фрейм для управления скриншотами."""

    def __init__(self, parent, screenshot_manager: ScreenshotManager, storage: PresetStorage):
        super().__init__(parent, text="📸 Скриншоты")
        self.screenshot_manager = screenshot_manager
        self.storage = storage
        self._setup_ui()
        self._refresh_screenshots()

    def _setup_ui(self) -> None:
        # Поиск скриншотов
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X)
        self.search_entry.insert(0, "🔍 Поиск скриншотов...")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)

        # Список скриншотов
        columns = ("name", "preset", "size", "created")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)

        self.tree.heading("name", text="Название")
        self.tree.heading("preset", text="Пресет")
        self.tree.heading("size", text="Размер")
        self.tree.heading("created", text="Создан")

        self.tree.column("name", width=200, minwidth=100)
        self.tree.column("preset", width=150, minwidth=80)
        self.tree.column("size", width=100, minwidth=60)
        self.tree.column("created", width=150, minwidth=100)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Кнопки управления
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="📸 Новый скриншот", command=self._create_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Редактировать", command=self._edit_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Удалить", command=self._delete_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📂 Открыть папку", command=self._open_folder).pack(side=tk.RIGHT, padx=5)

        self._selected_screenshot: Optional[ScreenshotInfo] = None

    def _on_search_focus_in(self, event):
        if self.search_var.get().startswith("🔍"):
            self.search_var.set("")

    def _on_search_focus_out(self, event):
        if not self.search_var.get():
            self.search_var.set("🔍 Поиск скриншотов...")

    def _on_search_changed(self, *args):
        query = self.search_var.get()
        if query.startswith("🔍"):
            query = ""
        self._filter_screenshots(query)

    def _refresh_screenshots(self) -> None:
        self._filter_screenshots(self.search_var.get() if not self.search_var.get().startswith("🔍") else "")

    def _filter_screenshots(self, query: str) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        screenshots = self.screenshot_manager.search_screenshots(query)
        for screenshot in screenshots:
            # Получаем связанный пресет (если есть)
            preset_name = self._get_preset_name_for_screenshot(screenshot.id)
            
            self.tree.insert("", tk.END, iid=screenshot.id, values=(
                screenshot.description or screenshot.id,
                preset_name or "-",
                f"{screenshot.width}x{screenshot.height}",
                screenshot.created_at.strftime("%d.%m.%Y %H:%M"),
            ))

    def _get_preset_name_for_screenshot(self, screenshot_id: str) -> Optional[str]:
        """Получает имя пресета, связанного со скриншотом."""
        # В будущем можно хранить связь в отдельном файле метаданных
        # Пока возвращаем None
        return None

    def _on_select(self, event) -> None:
        selection = self.tree.selection()
        if selection:
            screenshot_id = selection[0]
            self._selected_screenshot = self.screenshot_manager.get_screenshot(screenshot_id)

    def _on_double_click(self, event) -> None:
        self._view_screenshot()

    def _create_screenshot(self) -> None:
        """Открывает диалог для создания нового скриншота."""
        dialog = NewScreenshotDialog(self, self.screenshot_manager, self.storage)
        if dialog.result:
            self._refresh_screenshots()

    def _edit_screenshot(self) -> None:
        if self._selected_screenshot is None:
            messagebox.showwarning("Предупреждение", "Выберите скриншот для редактирования")
            return

        dialog = EditScreenshotDialog(self, self._selected_screenshot, self.storage)
        if dialog.result:
            # Обновляем описание в менеджере скриншотов
            # В будущем можно добавить полноценное редактирование метаданных
            self._refresh_screenshots()

    def _delete_screenshot(self) -> None:
        if self._selected_screenshot is None:
            messagebox.showwarning("Предупреждение", "Выберите скриншот для удаления")
            return

        if messagebox.askyesno("Подтверждение", f"Удалить скриншот '{self._selected_screenshot.description or self._selected_screenshot.id}'?"):
            self.screenshot_manager.remove_screenshot(self._selected_screenshot.id)
            self._selected_screenshot = None
            self._refresh_screenshots()

    def _view_screenshot(self) -> None:
        """Открывает скриншот в просмотрщике."""
        if self._selected_screenshot is None:
            return
            
        try:
            import os
            os.startfile(self._selected_screenshot.path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть скриншот: {e}")

    def _open_folder(self) -> None:
        """Открывает папку со скриншотами."""
        try:
            import os
            os.startfile(self.screenshot_manager.storage_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")


class NewScreenshotDialog(tk.Toplevel):
    """Диалог создания нового скриншота."""

    def __init__(self, parent, screenshot_manager: ScreenshotManager, storage: PresetStorage):
        super().__init__(parent)
        self.result: bool = False
        self.screenshot_manager = screenshot_manager
        self.storage = storage
        
        self.title("📸 Новый скриншот")
        self.geometry("500x450")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
        
        self.wait_window()

    def _setup_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Название скриншота
        ttk.Label(main_frame, text="📛 Название:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=8)
        
        # Выбор пресета (опционально)
        ttk.Label(main_frame, text="🔗 Привязать к пресету:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.preset_var = tk.StringVar()
        preset_combo = ttk.Combobox(main_frame, textvariable=self.preset_var, width=37, state="readonly")
        preset_combo.grid(row=1, column=1, pady=8)
        
        # Заполняем комбобокс доступными пресетами
        presets = self.storage.get_all_presets()
        preset_values = [""] + [p.name for p in presets]
        preset_combo["values"] = preset_values
        
        # Область выделения
        area_frame = ttk.LabelFrame(main_frame, text="📐 Область выделения")
        area_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10, ipadx=10, ipady=10)
        
        # Координаты
        coord_frame = ttk.Frame(area_frame)
        coord_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(coord_frame, text="X:").grid(row=0, column=0, padx=(0, 5))
        self.x_var = tk.StringVar(value="0")
        ttk.Entry(coord_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(coord_frame, text="Y:").grid(row=0, column=2, padx=(0, 5))
        self.y_var = tk.StringVar(value="0")
        ttk.Entry(coord_frame, textvariable=self.y_var, width=10).grid(row=0, column=3)
        
        # Размеры
        size_frame = ttk.Frame(area_frame)
        size_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(size_frame, text="Ширина:").grid(row=0, column=0, padx=(0, 5))
        self.width_var = tk.StringVar(value="800")
        ttk.Entry(size_frame, textvariable=self.width_var, width=10).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(size_frame, text="Высота:").grid(row=0, column=2, padx=(0, 5))
        self.height_var = tk.StringVar(value="600")
        ttk.Entry(size_frame, textvariable=self.height_var, width=10).grid(row=0, column=3)
        
        # Кнопка выбора области
        ttk.Button(area_frame, text="🎯 Выделить область мышью", command=self._select_area).pack(pady=10)
        
        # Описание
        ttk.Label(main_frame, text="📝 Описание:").grid(row=3, column=0, sticky=tk.NW, pady=8)
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(main_frame, textvariable=self.desc_var, width=40)
        desc_entry.grid(row=3, column=1, pady=8)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="✅ Сделать скриншот", command=self._capture).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ Отмена", command=self._cancel).pack(side=tk.LEFT, padx=10)
        
    def _select_area(self) -> None:
        """Открывает диалог для выделения области."""
        def on_confirm(area: tuple[int, int, int, int]):
            x, y, w, h = area
            self.x_var.set(str(x))
            self.y_var.set(str(y))
            self.width_var.set(str(w))
            self.height_var.set(str(h))
        
        dialog = ScreenshotAreaSelector(self, on_confirm)
        
    def _capture(self) -> None:
        """Делает скриншот с указанными параметрами."""
        try:
            name = self.name_var.get().strip()
            if not name:
                messagebox.showwarning("Предупреждение", "Введите название скриншота")
                return
                
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            w = int(self.width_var.get())
            h = int(self.height_var.get())
            
            if w <= 0 or h <= 0:
                messagebox.showwarning("Предупреждение", "Размеры области должны быть положительными")
                return
            
            description = self.desc_var.get().strip()
            
            # Генерируем ID на основе имени пресета (если указан) и названия
            preset_name = self.preset_var.get().strip()
            if preset_name:
                screenshot_id = f"{preset_name}_{name}"
            else:
                from datetime import datetime
                screenshot_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Заменяем недопустимые символы в ID
            screenshot_id = "".join(c if c.isalnum() or c in "_-" else "_" for c in screenshot_id)
            
            # Делаем скриншот
            self.screenshot_manager.capture(
                x=x, y=y, width=w, height=h,
                screenshot_id=screenshot_id,
                description=description
            )
            
            # Если указан пресет, сохраняем связь (в будущем можно сохранить в метаданные)
            if preset_name:
                # Здесь можно добавить логику сохранения связи скриншот-пресет
                pass
            
            self.result = True
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные значения: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сделать скриншот: {e}")
            
    def _cancel(self) -> None:
        self.destroy()


class EditScreenshotDialog(tk.Toplevel):
    """Диалог редактирования скриншота."""

    def __init__(self, parent, screenshot: ScreenshotInfo, storage: PresetStorage):
        super().__init__(parent)
        self.result: bool = False
        self.screenshot = screenshot
        self.storage = storage
        
        self.title("✏️ Редактировать скриншот")
        self.geometry("450x350")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
        
        self.wait_window()

    def _setup_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Название
        ttk.Label(main_frame, text="📛 Название:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.name_var = tk.StringVar(value=self.screenshot.description or self.screenshot.id)
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=8)
        
        # Информация о скриншоте
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Информация")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=10, ipadx=10, ipady=10)
        
        ttk.Label(info_frame, text=f"ID: {self.screenshot.id}").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Label(info_frame, text=f"Размер: {self.screenshot.width}x{self.screenshot.height}").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Label(info_frame, text=f"Позиция: ({self.screenshot.x}, {self.screenshot.y})").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Label(info_frame, text=f"Создан: {self.screenshot.created_at.strftime('%d.%m.%Y %H:%M')}").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Описание
        ttk.Label(main_frame, text="📝 Описание:").grid(row=2, column=0, sticky=tk.NW, pady=8)
        self.desc_var = tk.StringVar(value=self.screenshot.description)
        ttk.Entry(main_frame, textvariable=self.desc_var, width=40).grid(row=2, column=1, pady=8)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="✅ Сохранить", command=self._save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ Отмена", command=self._cancel).pack(side=tk.LEFT, padx=10)
        
    def _save(self) -> None:
        # В будущем можно добавить сохранение изменений
        self.result = True
        self.destroy()
        
    def _cancel(self) -> None:
        self.destroy()


class PresetManagerFrame(ttk.LabelFrame):
    """Фрейм для управления пресетами."""

    def __init__(self, parent, storage: PresetStorage, on_apply: Callable[[NormalizationPreset], bool]):
        super().__init__(parent, text="💾 Пресеты")
        self.storage = storage
        self.on_apply = on_apply
        self._setup_ui()
        self._refresh_presets()

    def _setup_ui(self) -> None:
        # Поиск пресетов
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X)
        self.search_entry.insert(0, "🔍 Поиск пресетов...")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)

        # Список пресетов
        columns = ("name", "process", "position")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)

        self.tree.heading("name", text="Имя")
        self.tree.heading("process", text="Процесс")
        self.tree.heading("position", text="Позиция/Размер")

        self.tree.column("name", width=160, minwidth=100)
        self.tree.column("process", width=120, minwidth=80)
        self.tree.column("position", width=170, minwidth=120)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Кнопки управления
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="▶ Применить", command=self._apply_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Редактировать", command=self._edit_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Удалить", command=self._delete_preset).pack(side=tk.LEFT, padx=5)

        self._selected_preset: Optional[NormalizationPreset] = None

    def _on_search_focus_in(self, event):
        if self.search_var.get().startswith("🔍"):
            self.search_var.set("")

    def _on_search_focus_out(self, event):
        if not self.search_var.get():
            self.search_var.set("🔍 Поиск пресетов...")

    def _on_search_changed(self, *args):
        query = self.search_var.get()
        if query.startswith("🔍"):
            query = ""
        self._filter_presets(query)

    def _refresh_presets(self) -> None:
        self._filter_presets(self.search_var.get() if not self.search_var.get().startswith("🔍") else "")

    def _filter_presets(self, query: str) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        presets = self.storage.search_presets(query)
        for preset in presets:
            self.tree.insert("", tk.END, iid=preset.id, values=(
                preset.name,
                preset.process_name,
                f"({preset.x}, {preset.y}) {preset.width}x{preset.height}",
            ))

    def _on_select(self, event) -> None:
        selection = self.tree.selection()
        if selection:
            preset_id = selection[0]
            self._selected_preset = self.storage.get_preset(preset_id)

    def _on_double_click(self, event) -> None:
        self._apply_preset()

    def _apply_preset(self) -> None:
        if self._selected_preset is None:
            messagebox.showwarning("Предупреждение", "Выберите пресет для применения")
            return

        if self.on_apply(self._selected_preset):
            messagebox.showinfo("Успех", f"Пресет '{self._selected_preset.name}' применен!")
        else:
            messagebox.showerror("Ошибка", f"Не удалось применить пресет. Окно '{self._selected_preset.process_name}' не найдено.")

    def _edit_preset(self) -> None:
        if self._selected_preset is None:
            messagebox.showwarning("Предупреждение", "Выберите пресет для редактирования")
            return

        dialog = EditPresetDialog(self, self._selected_preset)
        if dialog.result:
            self.storage.update_preset(
                preset_id=self._selected_preset.id,
                name=dialog.result.get("name"),
                process_name=dialog.result.get("process_name"),
                x=dialog.result.get("x"),
                y=dialog.result.get("y"),
                width=dialog.result.get("width"),
                height=dialog.result.get("height"),
                description=dialog.result.get("description"),
            )
            self._refresh_presets()

    def _delete_preset(self) -> None:
        if self._selected_preset is None:
            messagebox.showwarning("Предупреждение", "Выберите пресет для удаления")
            return

        if messagebox.askyesno("Подтверждение", f"Удалить пресет '{self._selected_preset.name}'?"):
            self.storage.remove_preset(self._selected_preset.id)
            self._selected_preset = None
            self._refresh_presets()


class EditPresetDialog(tk.Toplevel):
    """Диалог редактирования/создания пресета."""

    def __init__(self, parent, preset: Optional[NormalizationPreset] = None, prefill_data: Optional[dict] = None):
        super().__init__(parent)
        self.result: Optional[dict] = None
        self.preset = preset
        self.prefill_data = prefill_data

        self.title("✏️ Редактировать пресет" if preset else "💾 Новый пресет")
        self.geometry("450x400")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self._setup_ui()

        self.wait_window()

    def _setup_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Имя
        ttk.Label(main_frame, text="📛 Имя пресета:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.name_var = tk.StringVar(value=self.preset.name if self.preset else (self.prefill_data.get("name", "") if self.prefill_data else ""))
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=8)

        # Процесс
        ttk.Label(main_frame, text="🖥️ Процесс (часть заголовка):").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.process_var = tk.StringVar(value=self.preset.process_name if self.preset else (self.prefill_data.get("process_name", "") if self.prefill_data else ""))
        ttk.Entry(main_frame, textvariable=self.process_var, width=40).grid(row=1, column=1, pady=8)

        # Координаты
        coord_frame = ttk.Frame(main_frame)
        coord_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=8)
        
        ttk.Label(coord_frame, text="X:").grid(row=0, column=0, padx=(0, 5))
        self.x_var = tk.StringVar(value=str(self.preset.x) if self.preset else (str(self.prefill_data.get("x", 0)) if self.prefill_data else "0"))
        ttk.Entry(coord_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, padx=(0, 20))

        ttk.Label(coord_frame, text="Y:").grid(row=0, column=2, padx=(0, 5))
        self.y_var = tk.StringVar(value=str(self.preset.y) if self.preset else (str(self.prefill_data.get("y", 0)) if self.prefill_data else "0"))
        ttk.Entry(coord_frame, textvariable=self.y_var, width=10).grid(row=0, column=3)

        # Размеры
        size_frame = ttk.Frame(main_frame)
        size_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=8)
        
        ttk.Label(size_frame, text="Ширина:").grid(row=0, column=0, padx=(0, 5))
        self.width_var = tk.StringVar(value=str(self.preset.width) if self.preset else (str(self.prefill_data.get("width", 800)) if self.prefill_data else "800"))
        ttk.Entry(size_frame, textvariable=self.width_var, width=10).grid(row=0, column=1, padx=(0, 20))

        ttk.Label(size_frame, text="Высота:").grid(row=0, column=2, padx=(0, 5))
        self.height_var = tk.StringVar(value=str(self.preset.height) if self.preset else (str(self.prefill_data.get("height", 600)) if self.prefill_data else "600"))
        ttk.Entry(size_frame, textvariable=self.height_var, width=10).grid(row=0, column=3)

        # Описание
        ttk.Label(main_frame, text="📝 Описание:").grid(row=4, column=0, sticky=tk.NW, pady=8)
        self.desc_var = tk.StringVar(value=self.preset.description if self.preset else (self.prefill_data.get("description", "") if self.prefill_data else ""))
        ttk.Entry(main_frame, textvariable=self.desc_var, width=40).grid(row=4, column=1, pady=8)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="✅ Сохранить", command=self._save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ Отмена", command=self._cancel).pack(side=tk.LEFT, padx=10)

    def _save(self) -> None:
        try:
            self.result = {
                "name": self.name_var.get(),
                "process_name": self.process_var.get(),
                "x": int(self.x_var.get()),
                "y": int(self.y_var.get()),
                "width": int(self.width_var.get()),
                "height": int(self.height_var.get()),
                "description": self.desc_var.get(),
            }
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные числовые значения: {e}")

    def _cancel(self) -> None:
        self.destroy()


class NormalizerApp(ttk.Frame):
    """Основное приложение для нормализации процессов с вкладками."""

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("🚀 Automizer - Нормализация процессов и скриншоты")
        self.root.geometry("1100x800")

        self.normalizer = ProcessNormalizer()
        self.storage = PresetStorage()
        self.screenshot_manager = ScreenshotManager()

        # Применяем современный стиль
        apply_modern_style(root)

        self._selected_window: Optional[WindowInfo] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Создаем вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка 1: Выбор процесса и настройка
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="📋 Выбор процесса")
        self._setup_tab1(tab1)

        # Вкладка 2: Пресеты
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="💾 Управление пресетами")
        self._setup_tab2(tab2)

        # Вкладка 3: Скриншоты
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="📸 Скриншоты")
        self._setup_tab3(tab3)

    def _setup_tab3(self, parent) -> None:
        """Настройка третьей вкладки - управление скриншотами."""
        self.screenshot_manager_frame = ScreenshotManagerFrame(parent, self.screenshot_manager, self.storage)
        self.screenshot_manager_frame.pack(fill=tk.BOTH, expand=True)

    def _setup_tab1(self, parent) -> None:
        """Настройка первой вкладки - выбор процесса и настройка позиции."""
        # Верхняя часть - выбор процесса и позиция
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Левая колонка - выбор процесса
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.process_selector = ProcessSelectorFrame(left_frame, on_select=self._on_process_selected)
        self.process_selector.pack(fill=tk.BOTH, expand=True)

        # Правая колонка - позиция и размер
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.position_size_frame = PositionSizeFrame(right_frame)
        self.position_size_frame.pack(fill=tk.X, pady=(0, 15))

        # Кнопки действий
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X)

        ttk.Button(action_frame, text="✅ Нормализовать окно", command=self._normalize_window).pack(fill=tk.X, pady=3)
        ttk.Button(action_frame, text="💾 Сохранить как пресет", command=self._save_as_preset).pack(fill=tk.X, pady=3)

    def _setup_tab2(self, parent) -> None:
        """Настройка второй вкладки - управление пресетами."""
        self.preset_manager = PresetManagerFrame(parent, self.storage, on_apply=self._apply_preset)
        self.preset_manager.pack(fill=tk.BOTH, expand=True)

    def _on_process_selected(self, window: WindowInfo) -> None:
        self._selected_window = window
        self.position_size_frame.set_from_window(window)

    def _normalize_window(self) -> None:
        window = self.process_selector.get_selected_window()
        if window is None:
            messagebox.showwarning("⚠️ Предупреждение", "Выберите окно для нормализации")
            return

        try:
            x, y, width, height = self.position_size_frame.get_values()
        except ValueError as e:
            messagebox.showerror("❌ Ошибка", f"Некорректные значения: {e}")
            return

        if self.normalizer.normalize_window(window.window_id, x, y, width, height):
            messagebox.showinfo("✅ Успех", "Окно нормализовано!")
        else:
            messagebox.showerror("❌ Ошибка", "Не удалось нормализовать окно")

    def _save_as_preset(self) -> None:
        window = self.process_selector.get_selected_window()
        if window is None:
            messagebox.showwarning("⚠️ Предупреждение", "Выберите окно для создания пресета")
            return

        try:
            x, y, width, height = self.position_size_frame.get_values()
        except ValueError as e:
            messagebox.showerror("❌ Ошибка", f"Некорректные значения: {e}")
            return

        # Передаем текущие параметры окна в диалог
        prefill_data = {
            "name": window.title[:30] + "..." if len(window.title) > 30 else window.title,
            "process_name": window.title,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "description": "",
        }

        dialog = EditPresetDialog(self, prefill_data=prefill_data)
        if dialog.result:
            preset_id = f"preset_{len(self.storage.get_all_presets()) + 1}"
            try:
                self.storage.add_preset(
                    preset_id=preset_id,
                    name=dialog.result["name"],
                    process_name=dialog.result["process_name"],
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    description=dialog.result["description"],
                )
                self.preset_manager._refresh_presets()
                messagebox.showinfo("✅ Успех", "Пресет сохранен!")
                # Переключаемся на вкладку с пресетами
                self.notebook.select(1)
            except ValueError as e:
                messagebox.showerror("❌ Ошибка", str(e))

    def _apply_preset(self, preset: NormalizationPreset) -> bool:
        return self.normalizer.apply_preset(preset)


def main():
    """Запуск приложения."""
    root = tk.Tk()
    app = NormalizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
