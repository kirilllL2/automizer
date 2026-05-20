"""
Модуль для хранения настроек нормализации процессов.

Предоставляет функциональность для:
- Добавления пресетов нормализации
- Удаления пресетов
- Редактирования пресетов
- Получения списка пресетов
"""

import json
from pathlib import Path
from typing import Optional

from src.normalizer import NormalizationPreset


class PresetStorage:
    """Хранилище пресетов нормализации процессов."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            config_dir = Path.home() / ".automizer" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            storage_path = config_dir / "presets.json"

        self.storage_path = storage_path
        self._presets: dict[str, NormalizationPreset] = {}
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
                    preset_id: NormalizationPreset(**preset_data)
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
                "process_name": preset.process_name,
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
        process_name: str,
        x: int,
        y: int,
        width: int,
        height: int,
        description: str = "",
    ) -> NormalizationPreset:
        """
        Добавляет новый пресет.

        Args:
            preset_id: Уникальный идентификатор пресета.
            name: Отображаемое имя пресета.
            process_name: Имя процесса или часть заголовка.
            x: Координата X.
            y: Координата Y.
            width: Ширина.
            height: Высота.
            description: Описание пресета.

        Returns:
            Созданный пресет.

        Raises:
            ValueError: Если пресет с таким ID уже существует.
        """
        if preset_id in self._presets:
            raise ValueError(f"Пресет с ID '{preset_id}' уже существует")

        preset = NormalizationPreset(
            id=preset_id,
            name=name,
            process_name=process_name,
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
        process_name: Optional[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Optional[NormalizationPreset]:
        """
        Обновляет существующий пресет.

        Args:
            preset_id: Идентификатор пресета для обновления.
            name: Новое имя (None = не менять).
            process_name: Новое имя процесса (None = не менять).
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
        preset.process_name = process_name if process_name is not None else preset.process_name
        preset.x = x if x is not None else preset.x
        preset.y = y if y is not None else preset.y
        preset.width = width if width is not None else preset.width
        preset.height = height if height is not None else preset.height
        preset.description = description if description is not None else preset.description

        self.save()
        return preset

    def get_preset(self, preset_id: str) -> Optional[NormalizationPreset]:
        """
        Получает пресет по ID.

        Args:
            preset_id: Идентификатор пресета.

        Returns:
            Пресет или None, если не найден.
        """
        return self._presets.get(preset_id)

    def get_all_presets(self) -> list[NormalizationPreset]:
        """
        Получает все пресеты.

        Returns:
            Список всех пресетов.
        """
        return list(self._presets.values())

    def search_presets(self, query: str) -> list[NormalizationPreset]:
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
                search_term in preset.process_name.lower() or
                search_term in preset.description.lower())
        ]
