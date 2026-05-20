"""
UI модуль для управления нормализацией процессов.

Предоставляет Tkinter интерфейс для:
- Выбора процесса из списка с поиском
- Указания положения и размеров
- Управления пресетами (добавление, удаление, редактирование)
- Применения пресетов
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from src.window_manager import WindowManager, WindowInfo
from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.storage import PresetStorage


class ProcessSelectorFrame(ttk.LabelFrame):
    """Фрейм для выбора процесса с поиском."""

    def __init__(self, parent, on_select: Callable[[WindowInfo], None]):
        super().__init__(parent, text="Выберите процесс")
        self.on_select = on_select
        self._windows: list[WindowInfo] = []
        self._selected_window: Optional[WindowInfo] = None

        self._setup_ui()
        self._refresh_windows()

    def _setup_ui(self) -> None:
        # Поисковая строка
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)

        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.insert(0, "Поиск...")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)

        refresh_btn = ttk.Button(search_frame, text="⟳", command=self._refresh_windows)
        refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Список окон
        columns = ("title", "position", "size")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)

        self.tree.heading("title", text="Заголовок окна")
        self.tree.heading("position", text="Позиция")
        self.tree.heading("size", text="Размер")

        self.tree.column("title", width=300)
        self.tree.column("position", width=120)
        self.tree.column("size", width=100)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _on_search_focus_in(self, event):
        if self.search_var.get() == "Поиск...":
            self.search_var.set("")

    def _on_search_focus_out(self, event):
        if not self.search_var.get():
            self.search_var.set("Поиск...")

    def _on_search_changed(self, *args):
        query = self.search_var.get()
        if query == "Поиск...":
            query = ""
        self._filter_windows(query)

    def _refresh_windows(self) -> None:
        wm = WindowManager()
        self._windows = wm.get_windows()
        self._filter_windows(self.search_var.get() if self.search_var.get() != "Поиск..." else "")

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
        super().__init__(parent, text="Положение и размер")
        self._setup_ui()

    def _setup_ui(self) -> None:
        # Координаты
        coord_frame = ttk.Frame(self)
        coord_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(coord_frame, text="X:").grid(row=0, column=0, padx=(0, 5), sticky=tk.E)
        self.x_var = tk.StringVar(value="0")
        self.x_entry = ttk.Entry(coord_frame, textvariable=self.x_var, width=8)
        self.x_entry.grid(row=0, column=1, padx=(0, 15), sticky=tk.W)

        ttk.Label(coord_frame, text="Y:").grid(row=0, column=2, padx=(0, 5), sticky=tk.E)
        self.y_var = tk.StringVar(value="0")
        self.y_entry = ttk.Entry(coord_frame, textvariable=self.y_var, width=8)
        self.y_entry.grid(row=0, column=3, padx=(0, 15), sticky=tk.W)

        # Размеры
        size_frame = ttk.Frame(self)
        size_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(size_frame, text="Ширина:").grid(row=0, column=0, padx=(0, 5), sticky=tk.E)
        self.width_var = tk.StringVar(value="800")
        self.width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=8)
        self.width_entry.grid(row=0, column=1, padx=(0, 15), sticky=tk.W)

        ttk.Label(size_frame, text="Высота:").grid(row=0, column=2, padx=(0, 5), sticky=tk.E)
        self.height_var = tk.StringVar(value="600")
        self.height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=8)
        self.height_entry.grid(row=0, column=3, padx=(0, 15), sticky=tk.W)

        # Кнопки предустановок
        preset_frame = ttk.Frame(self)
        preset_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(preset_frame, text="Половина экрана ←", command=self._set_half_left).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Половина экрана →", command=self._set_half_right).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Четверть ↖", command=self._set_quarter_top_left).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Четверть ↗", command=self._set_quarter_top_right).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Четверть ↙", command=self._set_quarter_bottom_left).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Четверть ↘", command=self._set_quarter_bottom_right).pack(side=tk.LEFT, padx=2)

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


class PresetManagerFrame(ttk.LabelFrame):
    """Фрейм для управления пресетами."""

    def __init__(self, parent, storage: PresetStorage, on_apply: Callable[[NormalizationPreset], bool]):
        super().__init__(parent, text="Пресеты")
        self.storage = storage
        self.on_apply = on_apply
        self._setup_ui()
        self._refresh_presets()

    def _setup_ui(self) -> None:
        # Поиск пресетов
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X)
        self.search_entry.insert(0, "Поиск пресетов...")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)

        # Список пресетов
        columns = ("name", "process", "position")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=6)

        self.tree.heading("name", text="Имя")
        self.tree.heading("process", text="Процесс")
        self.tree.heading("position", text="Позиция/Размер")

        self.tree.column("name", width=150)
        self.tree.column("process", width=100)
        self.tree.column("position", width=150)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Кнопки управления
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Применить", command=self._apply_preset).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Редактировать", command=self._edit_preset).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить", command=self._delete_preset).pack(side=tk.LEFT, padx=2)

        self._selected_preset: Optional[NormalizationPreset] = None

    def _on_search_focus_in(self, event):
        if self.search_var.get() == "Поиск пресетов...":
            self.search_var.set("")

    def _on_search_focus_out(self, event):
        if not self.search_var.get():
            self.search_var.set("Поиск пресетов...")

    def _on_search_changed(self, *args):
        query = self.search_var.get()
        if query == "Поиск пресетов...":
            query = ""
        self._filter_presets(query)

    def _refresh_presets(self) -> None:
        self._filter_presets(self.search_var.get() if self.search_var.get() != "Поиск пресетов..." else "")

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

    def __init__(self, parent, preset: Optional[NormalizationPreset] = None):
        super().__init__(parent)
        self.result: Optional[dict] = None
        self.preset = preset

        self.title("Редактировать пресет" if preset else "Новый пресет")
        self.geometry("400x350")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self._setup_ui()

        self.wait_window()

    def _setup_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Имя
        ttk.Label(main_frame, text="Имя пресета:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.preset.name if self.preset else "")
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5)

        # Процесс
        ttk.Label(main_frame, text="Процесс (часть заголовка):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.process_var = tk.StringVar(value=self.preset.process_name if self.preset else "")
        ttk.Entry(main_frame, textvariable=self.process_var, width=40).grid(row=1, column=1, pady=5)

        # Координаты
        ttk.Label(main_frame, text="X:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.x_var = tk.StringVar(value=str(self.preset.x) if self.preset else "0")
        ttk.Entry(main_frame, textvariable=self.x_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Y:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.y_var = tk.StringVar(value=str(self.preset.y) if self.preset else "0")
        ttk.Entry(main_frame, textvariable=self.y_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5)

        # Размеры
        ttk.Label(main_frame, text="Ширина:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value=str(self.preset.width) if self.preset else "800")
        ttk.Entry(main_frame, textvariable=self.width_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Высота:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.StringVar(value=str(self.preset.height) if self.preset else "600")
        ttk.Entry(main_frame, textvariable=self.height_var, width=10).grid(row=5, column=1, sticky=tk.W, pady=5)

        # Описание
        ttk.Label(main_frame, text="Описание:").grid(row=6, column=0, sticky=tk.NW, pady=5)
        self.desc_var = tk.StringVar(value=self.preset.description if self.preset else "")
        ttk.Entry(main_frame, textvariable=self.desc_var, width=40).grid(row=6, column=1, pady=5)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Сохранить", command=self._save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self._cancel).pack(side=tk.LEFT, padx=10)

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
    """Основное приложение для нормализации процессов."""

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("Automizer - Нормализация процессов")
        self.root.geometry("900x700")

        self.normalizer = ProcessNormalizer()
        self.storage = PresetStorage()

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Верхняя часть - выбор процесса и позиция
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Левая колонка - выбор процесса
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.process_selector = ProcessSelectorFrame(left_frame, on_select=self._on_process_selected)
        self.process_selector.pack(fill=tk.BOTH, expand=True)

        # Правая колонка - позиция и размер
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.position_size_frame = PositionSizeFrame(right_frame)
        self.position_size_frame.pack(fill=tk.X, pady=(0, 10))

        # Кнопки действий
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X)

        ttk.Button(action_frame, text="Нормализовать окно", command=self._normalize_window).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Сохранить как пресет", command=self._save_as_preset).pack(fill=tk.X, pady=2)

        # Нижняя часть - управление пресетами
        self.preset_manager = PresetManagerFrame(self, self.storage, on_apply=self._apply_preset)
        self.preset_manager.pack(fill=tk.BOTH, expand=True)

    def _on_process_selected(self, window: WindowInfo) -> None:
        self.position_size_frame.set_from_window(window)

    def _normalize_window(self) -> None:
        window = self.process_selector.get_selected_window()
        if window is None:
            messagebox.showwarning("Предупреждение", "Выберите окно для нормализации")
            return

        try:
            x, y, width, height = self.position_size_frame.get_values()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные значения: {e}")
            return

        if self.normalizer.normalize_window(window.window_id, x, y, width, height):
            messagebox.showinfo("Успех", "Окно нормализовано!")
        else:
            messagebox.showerror("Ошибка", "Не удалось нормализовать окно")

    def _save_as_preset(self) -> None:
        window = self.process_selector.get_selected_window()
        if window is None:
            messagebox.showwarning("Предупреждение", "Выберите окно для создания пресета")
            return

        try:
            x, y, width, height = self.position_size_frame.get_values()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные значения: {e}")
            return

        dialog = EditPresetDialog(self)
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
                messagebox.showinfo("Успех", "Пресет сохранен!")
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))

    def _apply_preset(self, preset: NormalizationPreset) -> bool:
        return self.normalizer.apply_preset(preset)


def main():
    """Запуск приложения."""
    root = tk.Tk()
    app = NormalizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
