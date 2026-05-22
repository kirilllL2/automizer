"""
Модуль для хранения пресетов скриншотов.

Предоставляет функциональность для:
- Добавления пресетов скриншотов
- Удаления пресетов
- Редактирования пресетов
- Получения списка пресетов
- Быстрого создания скриншота по пресету
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.screenshot import ScreenshotManager, ScreenshotInfo


@dataclass
class ScreenshotPreset:
    """Пресет для создания скриншота."""

    id: str
    name: str
    screenshot_path: str  # Путь к файлу изображения (например: presets/screenshots/my_preset.png)
    process_preset_id: str  # ID связанного пресета нормализации
    x: int
    y: int
    width: int
    height: int
    description: str = ""

    def __repr__(self) -> str:
        return f"ScreenshotPreset(id={self.id}, name='{self.name}', process='{self.process_preset_id}')"


class ScreenshotPresetStorage:
    """Хранилище пресетов скриншотов."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            # Используем путь в репозитории для хранения пресетов
            repo_root = Path(__file__).parent.parent.parent
            presets_dir = repo_root / "presets"
            presets_dir.mkdir(parents=True, exist_ok=True)
            storage_path = presets_dir / "screenshot_presets.json"

        self.storage_path = storage_path
        self._presets: dict[str, ScreenshotPreset] = {}
        self.load()

    def load(self) -> None:
        """Загружает пресеты из файла."""
        if not self.storage_path.exists():
            self._presets = {}
            return

        try:
            with open(self.storage_path, encoding="utf-8") as f:
                data = json.load(f)
                self._presets = {
                    preset_id: ScreenshotPreset(**preset_data)
                    for preset_id, preset_data in data.items()
                }
        except (json.JSONDecodeError, KeyError, TypeError):
            self._presets = {}

    def save(self) -> None:
        """Сохраняет пресеты в файл."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            preset_id: {
                "id": preset.id,
                "name": preset.name,
                "screenshot_path": preset.screenshot_path,
                "process_preset_id": preset.process_preset_id,
                "x": preset.x,
                "y": preset.y,
                "width": preset.width,
                "height": preset.height,
                "description": preset.description,
            }
            for preset_id, preset in self._presets.items()
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_preset(
        self,
        preset_id: str,
        name: str,
        screenshot_path: str,
        process_preset_id: str,
        x: int,
        y: int,
        width: int,
        height: int,
        description: str = "",
    ) -> ScreenshotPreset:
        """
        Добавляет новый пресет скриншота.

        Args:
            preset_id: Уникальный идентификатор пресета.
            name: Отображаемое имя пресета.
            screenshot_path: Путь для сохранения скриншота.
            process_preset_id: ID связанного пресета нормализации.
            x: Координата X области скриншота.
            y: Координата Y области скриншота.
            width: Ширина области скриншота.
            height: Высота области скриншота.
            description: Описание пресета.

        Returns:
            Созданный пресет.

        Raises:
            ValueError: Если пресет с таким ID уже существует.
        """
        if preset_id in self._presets:
            raise ValueError(f"Пресет с ID '{preset_id}' уже существует")

        preset = ScreenshotPreset(
            id=preset_id,
            name=name,
            screenshot_path=screenshot_path,
            process_preset_id=process_preset_id,
            x=x,
            y=y,
            width=width,
            height=height,
            description=description,
        )
        self._presets[preset_id] = preset
        self.save()
        return preset

    def remove_preset(self, preset_id: str) -> bool:
        """
        Удаляет пресет.

        Args:
            preset_id: Идентификатор пресета для удаления.

        Returns:
            True, если пресет удален, False если не найден.
        """
        if preset_id not in self._presets:
            return False

        del self._presets[preset_id]
        self.save()
        return True

    def update_preset(
        self,
        preset_id: str,
        name: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        process_preset_id: Optional[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Optional[ScreenshotPreset]:
        """
        Обновляет существующий пресет.

        Args:
            preset_id: Идентификатор пресета для обновления.
            name: Новое имя (None = не менять).
            screenshot_path: Новый путь (None = не менять).
            process_preset_id: Новый ID пресета процесса (None = не менять).
            x: Новая координата X (None = не менять).
            y: Новая координата Y (None = не менять).
            width: Новая ширина (None = не менять).
            height: Новая высота (None = не менять).
            description: Новое описание (None = не менять).

        Returns:
            Обновленный пресет или None, если пресет не найден.
        """
        if preset_id not in self._presets:
            return None

        preset = self._presets[preset_id]
        preset.name = name if name is not None else preset.name
        preset.screenshot_path = screenshot_path if screenshot_path is not None else preset.screenshot_path
        preset.process_preset_id = process_preset_id if process_preset_id is not None else preset.process_preset_id
        preset.x = x if x is not None else preset.x
        preset.y = y if y is not None else preset.y
        preset.width = width if width is not None else preset.width
        preset.height = height if height is not None else preset.height
        preset.description = description if description is not None else preset.description

        self.save()
        return preset

    def get_preset(self, preset_id: str) -> Optional[ScreenshotPreset]:
        """
        Получает пресет по ID.

        Args:
            preset_id: Идентификатор пресета.

        Returns:
            Пресет или None, если не найден.
        """
        return self._presets.get(preset_id)

    def get_all_presets(self) -> list[ScreenshotPreset]:
        """
        Получает все пресеты.

        Returns:
            Список всех пресетов.
        """
        return list(self._presets.values())

    def search_presets(self, query: str) -> list[ScreenshotPreset]:
        """
        Ищет пресеты по запросу.

        Args:
            query: Поисковый запрос.

        Returns:
            Список найденных пресетов.
        """
        if not query:
            return self.get_all_presets()

        search_term = query.lower()
        return [
            preset for preset in self._presets.values()
            if (search_term in preset.name.lower() or
                search_term in preset.process_preset_id.lower() or
                search_term in preset.description.lower())
        ]

    def capture_with_preset(
        self,
        preset: ScreenshotPreset,
        screenshot_manager: ScreenshotManager,
    ) -> ScreenshotInfo:
        """
        Делает скриншот используя пресет.

        Скриншот сохраняется по пути, указанному в пресете (screenshot_path).
        Если файл уже существует, он будет перезаписан.

        Args:
            preset: Пресет для использования.
            screenshot_manager: Менеджер скриншотов.

        Returns:
            Информация о созданном/обновленном скриншоте.
        """
        # Используем ID пресета как ID скриншота для обеспечения соответствия 1:1
        screenshot_id = preset.id
        
        return screenshot_manager.capture(
            x=preset.x,
            y=preset.y,
            width=preset.width,
            height=preset.height,
            screenshot_id=screenshot_id,
            description=f"Скриншот по пресету '{preset.name}'",
            output_path=preset.screenshot_path,
        )
