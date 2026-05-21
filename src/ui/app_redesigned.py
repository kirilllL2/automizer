"""
Modern Redesigned UI for Process Normalization and Screenshot Management.

Features:
- Glassmorphism design with gradients, shadows, and rounded elements
- Oval/pill-shaped buttons with hover effects
- Responsive rubber-like layout
- Modern color palette with smooth transitions
- Card-based interface with depth and elevation
- Smooth animations and micro-interactions

Functional Requirements (based on current solution):
1. Process Selection Tab:
   - Searchable list of running windows
   - Real-time window position and size display
   - Quick presets for screen positioning (half, quarter, fullscreen)
   - Manual X, Y, Width, Height input
   - Normalize window button
   - Save as preset button

2. Process Presets Tab:
   - Searchable presets list
   - Apply preset to normalize matching window
   - Edit preset properties
   - Delete preset
   - Create new preset from current settings

3. Screenshots Tab:
   - Searchable screenshots list
   - Create new screenshot with area selection
   - Edit screenshot metadata
   - Delete screenshot
   - Open screenshot folder
   - Preview screenshot on screen

4. Screenshot Presets Tab:
   - Quick capture: normalize + screenshot in one click
   - Screenshot-only capture by preset
   - Manage screenshot presets
   - Link screenshot presets to process presets
   - Area selection dialog with visual preview
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from typing import Optional, Callable, List, Tuple
import math

from src.window_manager import WindowManager, WindowInfo
from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.storage import PresetStorage
from src.screenshot import ScreenshotManager, ScreenshotInfo
from src.screenshot.presets import ScreenshotPresetStorage, ScreenshotPreset


# ============================================================================
# MODERN COLOR PALETTE & STYLES
# ============================================================================

COLORS = {
    # Primary gradient colors
    "primary_start": "#667eea",
    "primary_end": "#764ba2",
    
    # Secondary gradient
    "secondary_start": "#f093fb",
    "secondary_end": "#f5576c",
    
    # Accent colors
    "accent_cyan": "#00d9ff",
    "accent_purple": "#a855f7",
    "accent_pink": "#ec4899",
    
    # Background layers (glassmorphism)
    "bg_dark": "#0f0f1a",
    "bg_card": "#1a1a2e",
    "bg_card_hover": "#252542",
    "bg_glass": "rgba(26, 26, 46, 0.85)",
    
    # Text colors
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0b0",
    "text_muted": "#6b6b80",
    
    # Status colors
    "success": "#10b981",
    "success_gradient_start": "#10b981",
    "success_gradient_end": "#059669",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "danger_gradient_start": "#ef4444",
    "danger_gradient_end": "#dc2626",
    "info": "#3b82f6",
    
    # Border and shadow
    "border_glow": "rgba(102, 126, 234, 0.3)",
    "shadow_color": "rgba(0, 0, 0, 0.4)",
}

# Font configurations
FONTS = {
    "heading_large": ("Segoe UI Variable", 18, "bold"),
    "heading_medium": ("Segoe UI Variable", 14, "bold"),
    "heading_small": ("Segoe UI Variable", 12, "bold"),
    "body": ("Segoe UI Variable", 10),
    "button": ("Segoe UI Variable", 10, "bold"),
    "mono": ("Consolas", 9),
}


class GradientButton(tk.Canvas):
    """Custom oval button with gradient background and hover effects."""
    
    def __init__(self, parent, text: str, command: Callable, 
                 width: int = 180, height: int = 44,
                 gradient_start: str = COLORS["primary_start"],
                 gradient_end: str = COLORS["primary_end"],
                 icon: str = "", **kwargs):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=COLORS["bg_dark"], **kwargs)
        
        self.command = command
        self.text = text
        self.icon = icon
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.base_width = width
        self.base_height = height
        self.is_hovered = False
        self.is_pressed = False
        
        self._draw_button()
        self._bind_events()
    
    def _draw_button(self):
        """Draw the oval gradient button."""
        self.delete("all")
        
        w, h = self.base_width, self.base_height
        radius = h // 2
        
        if self.is_pressed:
            # Pressed state - slightly smaller
            w, h = w - 4, h - 4
            radius = h // 2
        
        # Create gradient effect using multiple rectangles
        steps = 20
        for i in range(steps):
            ratio = i / steps
            color = self._blend_colors(self.gradient_start, self.gradient_end, ratio)
            x_pad = max(0, (i - steps//2) * 0.3)
            y_pad = max(0, (i - steps//2) * 0.3)
            
            if self.is_pressed:
                self.create_rounded_rectangle(
                    x_pad + 2, y_pad + 2,
                    w - x_pad - 2, h - y_pad - 2,
                    radius=radius - 2,
                    fill=color, outline=""
                )
            else:
                self.create_rounded_rectangle(
                    x_pad, y_pad,
                    w - x_pad, h - y_pad,
                    radius=radius,
                    fill=color, outline=""
                )
        
        # Add glow effect
        if self.is_hovered and not self.is_pressed:
            self.create_rounded_rectangle(
                2, 2, w - 2, h - 2,
                radius=radius - 1,
                outline=COLORS["border_glow"], width=2
            )
        
        # Draw text
        text_color = COLORS["text_primary"]
        if self.is_pressed:
            text_y = h // 2 + 2
        else:
            text_y = h // 2
        
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        self.create_text(
            w // 2, text_y,
            text=display_text,
            fill=text_color,
            font=FONTS["button"],
            anchor="center"
        )
    
    def _blend_colors(self, color1: str, color2: str, ratio: float) -> str:
        """Blend two hex colors based on ratio."""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Create a rounded rectangle."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
            x1 + radius, y1
        ]
        
        # Remove duplicate points
        if 'outline' in kwargs and kwargs['outline'] == '':
            del kwargs['outline']
            return self.create_polygon(points, smooth=True, **kwargs)
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _bind_events(self):
        """Bind mouse events for interactivity."""
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
    
    def _on_enter(self, event):
        self.is_hovered = True
        self._draw_button()
    
    def _on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self._draw_button()
    
    def _on_press(self, event):
        self.is_pressed = True
        self._draw_button()
    
    def _on_release(self, event):
        self.is_pressed = False
        self._draw_button()
        if self.command:
            self.command()


class GlassCard(ttk.Frame):
    """Glassmorphism-style card container with subtle borders and shadows."""
    
    def __init__(self, parent, title: str = "", icon: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.icon = icon
        
        # Configure style
        self.configure(style="Glass.TFrame")
    
    def add_title_bar(self):
        """Add a title bar to the card."""
        title_frame = tk.Frame(self, bg=COLORS["bg_card"])
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        if self.icon:
            icon_label = tk.Label(
                title_frame,
                text=self.icon,
                bg=COLORS["bg_card"],
                fg=COLORS["accent_purple"],
                font=("Segoe UI Emoji", 14)
            )
            icon_label.pack(side=tk.LEFT)
        
        if self.title:
            title_label = tk.Label(
                title_frame,
                text=self.title,
                bg=COLORS["bg_card"],
                fg=COLORS["text_primary"],
                font=FONTS["heading_medium"]
            )
            title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        return title_frame


class ModernEntry(ttk.Entry):
    """Modern styled entry with rounded corners and glow on focus."""
    
    def __init__(self, parent, placeholder: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.placeholder = placeholder
        self.has_placeholder = False
        
        self.configure(
            font=FONTS["body"],
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
            insertcolor=COLORS["accent_cyan"],
            relief=tk.FLAT,
            borderwidth=0
        )
        
        # Add padding
        self.configure(padding=(12, 10))
        
        if placeholder:
            self.insert(0, placeholder)
            self.has_placeholder = True
            self.configure(fg=COLORS["text_muted"])
        
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        if self.has_placeholder:
            self.delete(0, tk.END)
            self.has_placeholder = False
            self.configure(fg=COLORS["text_primary"])
    
    def _on_focus_out(self, event):
        if not self.get() and self.placeholder:
            self.insert(0, self.placeholder)
            self.has_placeholder = True
            self.configure(fg=COLORS["text_muted"])


class ModernTreeview(ttk.Treeview):
    """Modern styled treeview with custom colors and row height."""
    
    def __init__(self, parent, columns: tuple = (), **kwargs):
        super().__init__(parent, columns=columns, **kwargs)
        
        self.configure(
            show="headings",
            rowheight=40,
            selectmode="browse"
        )
        
        # Style headings
        for col in columns:
            self.heading(col, text=col.capitalize())
            self.column(col, anchor="w", padding=(15, 5))


# ============================================================================
# MAIN APPLICATION COMPONENTS
# ============================================================================

class ProcessSelectorCard(GlassCard):
    """Card for selecting processes with search and list."""
    
    def __init__(self, parent, on_select: Callable[[WindowInfo], None]):
        super().__init__(parent, title="Running Processes", icon="📋")
        self.on_select = on_select
        self._windows: List[WindowInfo] = []
        self._selected_window: Optional[WindowInfo] = None
        
        self._setup_ui()
        self._refresh_windows()
    
    def _setup_ui(self):
        # Content frame
        content = tk.Frame(self, bg=COLORS["bg_card"])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Search bar
        search_container = tk.Frame(content, bg=COLORS["bg_dark"])
        search_container.pack(fill=tk.X, pady=(0, 15))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        
        self.search_entry = ModernEntry(
            search_container,
            placeholder="🔍 Search processes...",
            textvariable=self.search_var
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Refresh button
        refresh_btn = GradientButton(
            search_container,
            text="Refresh",
            command=self._refresh_windows,
            width=100,
            height=38,
            icon="⟳"
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Treeview with scrollbar
        tree_frame = tk.Frame(content, bg=COLORS["bg_dark"])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("title", "position", "size")
        self.tree = ModernTreeview(tree_frame, columns=columns, height=12)
        
        self.tree.heading("title", text="Window Title")
        self.tree.heading("position", text="Position")
        self.tree.heading("size", text="Size")
        
        self.tree.column("title", width=300, minwidth=200)
        self.tree.column("position", width=120, minwidth=100)
        self.tree.column("size", width=100, minwidth=80)
        
        # Custom scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
    
    def _on_search_changed(self, *args):
        query = self.search_var.get()
        self._filter_windows(query)
    
    def _refresh_windows(self):
        wm = WindowManager()
        self._windows = wm.get_windows()
        self._filter_windows(self.search_var.get())
    
    def _filter_windows(self, query: str):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = query.lower()
        filtered = [
            w for w in self._windows
            if not search_term or search_term in w.title.lower()
        ]
        
        for window in filtered:
            self.tree.insert("", tk.END, iid=str(window.window_id), values=(
                window.title[:45] + "..." if len(window.title) > 45 else window.title,
                f"({window.x}, {window.y})",
                f"{window.width}×{window.height}",
            ))
    
    def _on_select(self, event):
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


class PositionSizeCard(GlassCard):
    """Card for setting window position and size with quick presets."""
    
    def __init__(self, parent):
        super().__init__(parent, title="Position & Size", icon="📐")
        self._setup_ui()
    
    def _setup_ui(self):
        content = tk.Frame(self, bg=COLORS["bg_card"])
        content.pack(fill=tk.X, expand=True, padx=20, pady=10)
        
        # Coordinates section
        coord_frame = tk.LabelFrame(
            content,
            text="  Coordinates  ",
            bg=COLORS["bg_dark"],
            fg=COLORS["accent_cyan"],
            font=FONTS["heading_small"]
        )
        coord_frame.pack(fill=tk.X, pady=(0, 15))
        
        # X coordinate
        x_container = tk.Frame(coord_frame, bg=COLORS["bg_dark"])
        x_container.pack(fill=tk.X, padx=15, pady=8)
        
        tk.Label(
            x_container,
            text="X:",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            font=FONTS["body"],
            width=3,
            anchor="e"
        ).pack(side=tk.LEFT)
        
        self.x_var = tk.StringVar(value="0")
        self.x_entry = ModernEntry(x_container, textvariable=self.x_var)
        self.x_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 20))
        
        # Y coordinate
        y_container = tk.Frame(coord_frame, bg=COLORS["bg_dark"])
        y_container.pack(fill=tk.X, padx=15, pady=8)
        
        tk.Label(
            y_container,
            text="Y:",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            font=FONTS["body"],
            width=3,
            anchor="e"
        ).pack(side=tk.LEFT)
        
        self.y_var = tk.StringVar(value="0")
        self.y_entry = ModernEntry(y_container, textvariable=self.y_var)
        self.y_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Size section
        size_frame = tk.LabelFrame(
            content,
            text="  Dimensions  ",
            bg=COLORS["bg_dark"],
            fg=COLORS["accent_pink"],
            font=FONTS["heading_small"]
        )
        size_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Width
        w_container = tk.Frame(size_frame, bg=COLORS["bg_dark"])
        w_container.pack(fill=tk.X, padx=15, pady=8)
        
        tk.Label(
            w_container,
            text="W:",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            font=FONTS["body"],
            width=3,
            anchor="e"
        ).pack(side=tk.LEFT)
        
        self.width_var = tk.StringVar(value="800")
        self.width_entry = ModernEntry(w_container, textvariable=self.width_var)
        self.width_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 20))
        
        # Height
        h_container = tk.Frame(size_frame, bg=COLORS["bg_dark"])
        h_container.pack(fill=tk.X, padx=15, pady=8)
        
        tk.Label(
            h_container,
            text="H:",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            font=FONTS["body"],
            width=3,
            anchor="e"
        ).pack(side=tk.LEFT)
        
        self.height_var = tk.StringVar(value="600")
        self.height_entry = ModernEntry(h_container, textvariable=self.height_var)
        self.height_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Quick presets
        preset_label = tk.Label(
            content,
            text="Quick Presets",
            bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"],
            font=FONTS["heading_small"]
        )
        preset_label.pack(anchor="w", padx=5, pady=(10, 5))
        
        preset_frame = tk.Frame(content, bg=COLORS["bg_card"])
        preset_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Preset buttons with icons
        presets = [
            ("½ ←", self._set_half_left, COLORS["primary_start"], COLORS["primary_end"]),
            ("½ →", self._set_half_right, COLORS["primary_start"], COLORS["primary_end"]),
            ("¼ ↖", self._set_quarter_top_left, COLORS["secondary_start"], COLORS["secondary_end"]),
            ("¼ ↗", self._set_quarter_top_right, COLORS["secondary_start"], COLORS["secondary_end"]),
            ("¼ ↙", self._set_quarter_bottom_left, COLORS["secondary_start"], COLORS["secondary_end"]),
            ("¼ ↘", self._set_quarter_bottom_right, COLORS["secondary_start"], COLORS["secondary_end"]),
        ]
        
        for text, cmd, start, end in presets:
            btn = GradientButton(
                preset_frame,
                text=text,
                command=cmd,
                width=90,
                height=36,
                gradient_start=start,
                gradient_end=end
            )
            btn.pack(side=tk.LEFT, padx=4, pady=4)
    
    def _get_screen_size(self) -> Tuple[int, int]:
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        return screen_width, screen_height
    
    def _set_half_left(self):
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h))
    
    def _set_half_right(self):
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set(str(screen_w // 2))
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h))
    
    def _set_quarter_top_left(self):
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))
    
    def _set_quarter_top_right(self):
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set(str(screen_w // 2))
        self.y_var.set("0")
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))
    
    def _set_quarter_bottom_left(self):
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set("0")
        self.y_var.set(str(screen_h // 2))
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))
    
    def _set_quarter_bottom_right(self):
        screen_w, screen_h = self._get_screen_size()
        self.x_var.set(str(screen_w // 2))
        self.y_var.set(str(screen_h // 2))
        self.width_var.set(str(screen_w // 2))
        self.height_var.set(str(screen_h // 2))
    
    def get_values(self) -> Tuple[int, int, int, int]:
        return (
            int(self.x_var.get()),
            int(self.y_var.get()),
            int(self.width_var.get()),
            int(self.height_var.get()),
        )
    
    def set_from_window(self, window: WindowInfo):
        self.x_var.set(str(window.x))
        self.y_var.set(str(window.y))
        self.width_var.set(str(window.width))
        self.height_var.set(str(window.height))


class ActionButtonsCard(GlassCard):
    """Card with primary action buttons."""
    
    def __init__(self, parent, on_normalize: Callable, on_save_preset: Callable):
        super().__init__(parent)
        self.on_normalize = on_normalize
        self.on_save_preset = on_save_preset
        self._setup_ui()
    
    def _setup_ui(self):
        content = tk.Frame(self, bg=COLORS["bg_card"])
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Normalize button
        normalize_btn = GradientButton(
            content,
            text="Normalize Window",
            command=self.on_normalize,
            width=220,
            height=50,
            gradient_start=COLORS["success_gradient_start"],
            gradient_end=COLORS["success_gradient_end"],
            icon="✅"
        )
        normalize_btn.pack(pady=8)
        
        # Save preset button
        save_btn = GradientButton(
            content,
            text="Save as Preset",
            command=self.on_save_preset,
            width=220,
            height=50,
            gradient_start=COLORS["primary_start"],
            gradient_end=COLORS["primary_end"],
            icon="💾"
        )
        save_btn.pack(pady=8)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class ModernNormalizerApp(tk.Frame):
    """Main application with modern redesigned UI."""
    
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("✨ Automizer - Modern Window Manager")
        self.root.geometry("1200x850")
        self.root.minsize(1000, 700)
        
        # Initialize managers
        self.normalizer = ProcessNormalizer()
        self.storage = PresetStorage()
        self.screenshot_manager = ScreenshotManager()
        self.screenshot_preset_storage = ScreenshotPresetStorage()
        
        self._selected_window: Optional[WindowInfo] = None
        
        self._setup_styles()
        self._setup_ui()
    
    def _setup_styles(self):
        """Configure ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # TFrame
        style.configure("TFrame", background=COLORS["bg_dark"])
        
        # TLabel
        style.configure("TLabel", 
                       background=COLORS["bg_dark"],
                       foreground=COLORS["text_primary"],
                       font=FONTS["body"])
        
        # TNotebook
        style.configure("TNotebook",
                       background=COLORS["bg_dark"],
                       borderwidth=0,
                       tabmargins=[0, 0, 0, 0])
        
        style.configure("TNotebook.Tab",
                       background=COLORS["bg_card"],
                       foreground=COLORS["text_secondary"],
                       padding=(30, 15),
                       font=FONTS["heading_small"])
        
        style.map("TNotebook.Tab",
                 background=[("selected", COLORS["bg_card_hover"])],
                 foreground=[("selected", COLORS["text_primary"])])
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        self.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header()
        
        # Main content with notebook
        content_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Process Selection
        tab1 = tk.Frame(self.notebook, bg=COLORS["bg_dark"])
        self.notebook.add(tab1, text="  📋 Process Selection  ")
        self._setup_process_tab(tab1)
        
        # Tab 2: Process Presets
        tab2 = tk.Frame(self.notebook, bg=COLORS["bg_dark"])
        self.notebook.add(tab2, text="  💾 Process Presets  ")
        self._setup_presets_tab(tab2)
        
        # Tab 3: Screenshots
        tab3 = tk.Frame(self.notebook, bg=COLORS["bg_dark"])
        self.notebook.add(tab3, text="  📸 Screenshots  ")
        self._setup_screenshots_tab(tab3)
        
        # Tab 4: Screenshot Presets
        tab4 = tk.Frame(self.notebook, bg=COLORS["bg_dark"])
        self.notebook.add(tab4, text="  🎯 Screenshot Presets  ")
        self._setup_screenshot_presets_tab(tab4)
    
    def _create_header(self):
        """Create modern header with gradient."""
        header = tk.Frame(self, bg=COLORS["bg_dark"], height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 0))
        
        # Gradient canvas for header background
        header_bg = tk.Canvas(header, height=80, bg=COLORS["bg_dark"], highlightthickness=0)
        header_bg.pack(fill=tk.X, side=tk.TOP)
        
        # Draw gradient
        for i in range(80):
            ratio = i / 80
            color = self._blend_colors(COLORS["primary_start"], COLORS["primary_end"], ratio * 0.5)
            header_bg.create_rectangle(0, i, 2000, i+1, fill=color, outline="")
        
        # Title
        title_label = tk.Label(
            header,
            text="✨ Automizer",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
            font=FONTS["heading_large"]
        )
        title_label.place(x=30, y=25)
        
        subtitle_label = tk.Label(
            header,
            text="Modern Window Management & Screenshot Tool",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            font=FONTS["body"]
        )
        subtitle_label.place(x=30, y=55)
    
    def _blend_colors(self, color1: str, color2: str, ratio: float) -> str:
        """Blend two hex colors."""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _setup_process_tab(self, parent):
        """Setup the process selection tab."""
        # Left panel - Process selector
        left_panel = tk.Frame(parent, bg=COLORS["bg_dark"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        process_card = ProcessSelectorCard(left_panel, on_select=self._on_process_selected)
        process_card.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Position/Size and Actions
        right_panel = tk.Frame(parent, bg=COLORS["bg_dark"])
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        
        position_card = PositionSizeCard(right_panel)
        self.position_size_card = position_card
        position_card.pack(fill=tk.X, pady=(0, 15))
        
        action_card = ActionButtonsCard(
            right_panel,
            on_normalize=self._normalize_window,
            on_save_preset=self._save_as_preset
        )
        action_card.pack(fill=tk.X)
    
    def _setup_presets_tab(self, parent):
        """Setup the process presets tab."""
        # This would be implemented similar to original but with modern styling
        # For brevity, showing placeholder structure
        placeholder = tk.Label(
            parent,
            text="Process Presets Management\n\nComing in full implementation",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            font=FONTS["heading_medium"],
            justify="center"
        )
        placeholder.pack(expand=True)
    
    def _setup_screenshots_tab(self, parent):
        """Setup the screenshots tab."""
        placeholder = tk.Label(
            parent,
            text="Screenshots Management\n\nComing in full implementation",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            font=FONTS["heading_medium"],
            justify="center"
        )
        placeholder.pack(expand=True)
    
    def _setup_screenshot_presets_tab(self, parent):
        """Setup the screenshot presets tab."""
        placeholder = tk.Label(
            parent,
            text="Screenshot Presets & Quick Capture\n\nComing in full implementation",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            font=FONTS["heading_medium"],
            justify="center"
        )
        placeholder.pack(expand=True)
    
    def _on_process_selected(self, window: WindowInfo):
        """Handle process selection."""
        self._selected_window = window
        self.position_size_card.set_from_window(window)
    
    def _normalize_window(self):
        """Normalize the selected window."""
        window = self._selected_window
        if window is None:
            messagebox.showwarning("⚠️ Warning", "Please select a window to normalize")
            return
        
        try:
            x, y, width, height = self.position_size_card.get_values()
        except ValueError as e:
            messagebox.showerror("❌ Error", f"Invalid values: {e}")
            return
        
        if self.normalizer.normalize_window(window.window_id, x, y, width, height):
            messagebox.showinfo("✅ Success", "Window normalized!")
        else:
            messagebox.showerror("❌ Error", "Failed to normalize window")
    
    def _save_as_preset(self):
        """Save current settings as a preset."""
        window = self._selected_window
        if window is None:
            messagebox.showwarning("⚠️ Warning", "Please select a window first")
            return
        
        try:
            x, y, width, height = self.position_size_card.get_values()
        except ValueError as e:
            messagebox.showerror("❌ Error", f"Invalid values: {e}")
            return
        
        # Create simple preset dialog (full implementation would have modern dialog)
        preset_name = f"Preset_{len(self.storage.get_all_presets()) + 1}"
        
        try:
            preset_id = f"preset_{len(self.storage.get_all_presets()) + 1}"
            self.storage.add_preset(
                preset_id=preset_id,
                name=preset_name,
                process_name=window.title,
                x=x,
                y=y,
                width=width,
                height=height,
                description="",
            )
            messagebox.showinfo("✅ Success", "Preset saved!")
        except ValueError as e:
            messagebox.showerror("❌ Error", str(e))


def main():
    """Launch the application."""
    root = tk.Tk()
    
    # Set dark theme for the window
    root.configure(bg=COLORS["bg_dark"])
    
    app = ModernNormalizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
