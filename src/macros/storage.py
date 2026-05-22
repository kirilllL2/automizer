"""
Модуль для хранения и управления макросами.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

from src.macros import MacroAction, action_from_dict, ActionType


class Macro:
    """Класс макроса - последовательности действий."""
    
    def __init__(
        self,
        macro_id: str,
        name: str,
        description: str = "",
        actions: Optional[list[MacroAction]] = None,
    ):
        self.id = macro_id
        self.name = name
        self.description = description
        self.actions = actions or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_action(self, action: MacroAction, index: Optional[int] = None) -> None:
        """Добавляет действие в макрос."""
        if index is not None:
            self.actions.insert(index, action)
        else:
            self.actions.append(action)
        self.updated_at = datetime.now()
    
    def remove_action(self, action_id: str) -> bool:
        """Удаляет действие по ID."""
        for i, action in enumerate(self.actions):
            if action.id == action_id:
                self.actions.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_action_by_id(self, action_id: str) -> Optional[MacroAction]:
        """Получает действие по ID."""
        for action in self.actions:
            if action.id == action_id:
                return action
        return None
    
    def get_action_by_label(self, label: str) -> Optional[MacroAction]:
        """Получает первое действие с указанным label."""
        for action in self.actions:
            if action.label == label:
                return action
        return None
    
    def get_all_labels(self) -> list[str]:
        """Получает все уникальные label в макросе."""
        labels = set()
        for action in self.actions:
            if action.label:
                labels.add(action.label)
        return sorted(labels)
    
    def to_dict(self) -> dict[str, Any]:
        """Сериализует макрос в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "actions": [action.to_dict() for action in self.actions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Macro":
        """Десериализует макрос из словаря."""
        macro = cls(
            macro_id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
        )
        
        # Парсим действия
        for action_data in data.get("actions", []):
            action = action_from_dict(action_data)
            macro.actions.append(action)
        
        # Восстанавливаем временные метки
        if "created_at" in data:
            macro.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            macro.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return macro
    
    def __repr__(self) -> str:
        return f"Macro(id={self.id}, name='{self.name}', actions={len(self.actions)})"


class MacroStorage:
    """Хранилище макросов."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            repo_root = Path(__file__).parent.parent.parent
            presets_dir = repo_root / "presets"
            presets_dir.mkdir(parents=True, exist_ok=True)
            storage_path = presets_dir / "macros.json"
        
        self.storage_path = storage_path
        self._macros: dict[str, Macro] = {}
        self.load()
    
    def load(self) -> None:
        """Загружает макросы из файла."""
        if not self.storage_path.exists():
            self._macros = {}
            return
        
        try:
            with open(self.storage_path, encoding="utf-8") as f:
                data = json.load(f)
                self._macros = {
                    macro_id: Macro.from_dict(macro_data)
                    for macro_id, macro_data in data.items()
                }
        except (json.JSONDecodeError, KeyError, TypeError):
            self._macros = {}
    
    def save(self) -> None:
        """Сохраняет макросы в файл."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            macro_id: macro.to_dict()
            for macro_id, macro in self._macros.items()
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_macro(self, macro: Macro) -> Macro:
        """Добавляет макрос в хранилище."""
        if macro.id in self._macros:
            raise ValueError(f"Макрос с ID '{macro.id}' уже существует")
        
        self._macros[macro.id] = macro
        self.save()
        return macro
    
    def remove_macro(self, macro_id: str) -> bool:
        """Удаляет макрос по ID."""
        if macro_id not in self._macros:
            return False
        
        del self._macros[macro_id]
        self.save()
        return True
    
    def update_macro(self, macro: Macro) -> Optional[Macro]:
        """Обновляет существующий макрос."""
        if macro.id not in self._macros:
            return None
        
        macro.updated_at = datetime.now()
        self._macros[macro.id] = macro
        self.save()
        return macro
    
    def get_macro(self, macro_id: str) -> Optional[Macro]:
        """Получает макрос по ID."""
        return self._macros.get(macro_id)
    
    def get_all_macros(self) -> list[Macro]:
        """Получает все макросы."""
        return list(self._macros.values())
    
    def search_macros(self, query: str) -> list[Macro]:
        """Ищет макросы по запросу."""
        if not query:
            return self.get_all_macros()
        
        search_term = query.lower()
        return [
            macro for macro in self._macros.values()
            if (search_term in macro.name.lower() or
                search_term in macro.description.lower() or
                search_term in macro.id.lower())
        ]
    
    def create_macro(
        self,
        macro_id: str,
        name: str,
        description: str = "",
    ) -> Macro:
        """Создает и добавляет новый макрос."""
        macro = Macro(
            macro_id=macro_id,
            name=name,
            description=description,
        )
        return self.add_macro(macro)
