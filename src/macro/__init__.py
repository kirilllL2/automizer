"""
Модуль бизнес-логики для работы с макросами.
Содержит модели действий, макросов и логику их выполнения.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time
import json
from pathlib import Path


class ActionType(Enum):
    """Типы доступных действий."""
    CLICK = "click"
    DELAY = "delay"


@dataclass
class MacroAction:
    """Базовый класс действия макроса."""
    id: str
    action_type: ActionType
    name: str
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализует действие в словарь."""
        return {
            "id": self.id,
            "action_type": self.action_type.value,
            "name": self.name,
            "enabled": self.enabled,
            "parameters": self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MacroAction":
        """Десериализует действие из словаря."""
        return cls(
            id=data["id"],
            action_type=ActionType(data["action_type"]),
            name=data["name"],
            enabled=data.get("enabled", True),
            parameters=data.get("parameters", {})
        )


@dataclass
class ClickAction(MacroAction):
    """Действие: клик в определенную точку."""
    x: int = 0
    y: int = 0
    
    def __init__(self, id: str, name: str, enabled: bool = True, x: int = 0, y: int = 0):
        super().__init__(id=id, action_type=ActionType.CLICK, name=name, enabled=enabled)
        self.x = x
        self.y = y
        self.parameters = {"x": self.x, "y": self.y}
    
    def execute(self) -> bool:
        """Выполняет клик в указанную точку."""
        if not self.enabled:
            return True
        
        try:
            from PyQt6.QtGui import QCursor
            from PyQt6.QtCore import QPoint
            
            cursor = QCursor()
            cursor.setPos(QPoint(self.x, self.y))
            # Симуляция клика будет добавлена позже
            print(f"[ClickAction] Клик в точке ({self.x}, {self.y})")
            return True
        except ImportError:
            # Если PyQt6 недоступен (тестирование без GUI)
            print(f"[ClickAction] Клик в точке ({self.x}, {self.y}) (симуляция)")
            return True
        except Exception as e:
            print(f"[ClickAction] Ошибка выполнения: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["parameters"] = {"x": self.x, "y": self.y}
        return data


@dataclass
class DelayAction(MacroAction):
    """Действие: задержка на n секунд."""
    duration: float = 1.0
    
    def __init__(self, id: str, name: str, enabled: bool = True, duration: float = 1.0):
        super().__init__(id=id, action_type=ActionType.DELAY, name=name, enabled=enabled)
        self.duration = duration
        self.parameters = {"duration": self.duration}
    
    def execute(self) -> bool:
        """Выполняет задержку."""
        if not self.enabled:
            return True
        
        try:
            print(f"[DelayAction] Задержка на {self.duration} сек.")
            time.sleep(self.duration)
            return True
        except Exception as e:
            print(f"[DelayAction] Ошибка выполнения: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["parameters"] = {"duration": self.duration}
        return data


@dataclass
class Macro:
    """Макрос - последовательность действий."""
    id: str
    name: str
    description: str = ""
    actions: List[MacroAction] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def add_action(self, action: MacroAction, index: Optional[int] = None):
        """Добавляет действие в макрос."""
        if index is not None:
            self.actions.insert(index, action)
        else:
            self.actions.append(action)
        self.updated_at = time.time()
    
    def remove_action(self, action_id: str) -> bool:
        """Удаляет действие по ID."""
        for i, action in enumerate(self.actions):
            if action.id == action_id:
                self.actions.pop(i)
                self.updated_at = time.time()
                return True
        return False
    
    def move_action(self, action_id: str, new_index: int) -> bool:
        """Перемещает действие на новую позицию."""
        for i, action in enumerate(self.actions):
            if action.id == action_id:
                action_obj = self.actions.pop(i)
                if new_index < 0:
                    new_index = 0
                if new_index >= len(self.actions):
                    new_index = len(self.actions)
                self.actions.insert(new_index, action_obj)
                self.updated_at = time.time()
                return True
        return False
    
    def execute(self) -> bool:
        """Выполняет все действия макроса последовательно."""
        print(f"[Macro] Запуск макроса '{self.name}'")
        for action in self.actions:
            if action.enabled:
                if not action.execute():
                    print(f"[Macro] Ошибка выполнения действия {action.name}")
                    return False
        print(f"[Macro] Макрос '{self.name}' завершен")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализует макрос в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "actions": [a.to_dict() for a in self.actions],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Macro":
        """Десериализует макрос из словаря."""
        macro = cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )
        
        for action_data in data.get("actions", []):
            action_type = ActionType(action_data["action_type"])
            
            if action_type == ActionType.CLICK:
                action = ClickAction(
                    id=action_data["id"],
                    name=action_data["name"],
                    enabled=action_data.get("enabled", True),
                    x=action_data.get("parameters", {}).get("x", 0),
                    y=action_data.get("parameters", {}).get("y", 0)
                )
            elif action_type == ActionType.DELAY:
                action = DelayAction(
                    id=action_data["id"],
                    name=action_data["name"],
                    enabled=action_data.get("enabled", True),
                    duration=action_data.get("parameters", {}).get("duration", 1.0)
                )
            else:
                # Неизвестный тип действия
                continue
            
            macro.actions.append(action)
        
        return macro


class MacroStorage:
    """Хранилище макросов."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "macros.json"
        self.storage_path = storage_path
        self.macros: Dict[str, Macro] = {}
        self._load()
    
    def _load(self):
        """Загружает макросы из файла."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for macro_data in data.get("macros", []):
                        macro = Macro.from_dict(macro_data)
                        self.macros[macro.id] = macro
                print(f"[MacroStorage] Загружено {len(self.macros)} макросов")
            except Exception as e:
                print(f"[MacroStorage] Ошибка загрузки: {e}")
    
    def _save(self):
        """Сохраняет макросы в файл."""
        try:
            data = {
                "macros": [m.to_dict() for m in self.macros.values()]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[MacroStorage] Сохранено {len(self.macros)} макросов")
        except Exception as e:
            print(f"[MacroStorage] Ошибка сохранения: {e}")
    
    def create_macro(self, name: str, description: str = "") -> Macro:
        """Создает новый макрос."""
        import uuid
        macro = Macro(
            id=str(uuid.uuid4()),
            name=name,
            description=description
        )
        self.macros[macro.id] = macro
        self._save()
        return macro
    
    def get_macro(self, macro_id: str) -> Optional[Macro]:
        """Получает макрос по ID."""
        return self.macros.get(macro_id)
    
    def update_macro(self, macro: Macro) -> bool:
        """Обновляет существующий макрос."""
        if macro.id in self.macros:
            macro.updated_at = time.time()
            self.macros[macro.id] = macro
            self._save()
            return True
        return False
    
    def delete_macro(self, macro_id: str) -> bool:
        """Удаляет макрос по ID."""
        if macro_id in self.macros:
            del self.macros[macro_id]
            self._save()
            return True
        return False
    
    def list_macros(self) -> List[Macro]:
        """Возвращает список всех макросов."""
        return list(self.macros.values())
    
    def execute_macro(self, macro_id: str) -> bool:
        """Выполняет макрос по ID."""
        macro = self.get_macro(macro_id)
        if macro:
            return macro.execute()
        return False


# Фабрика действий
def create_action(action_type: ActionType, name: str, **kwargs) -> MacroAction:
    """Фабричный метод для создания действий."""
    import uuid
    
    if action_type == ActionType.CLICK:
        return ClickAction(
            id=str(uuid.uuid4()),
            name=name,
            x=kwargs.get("x", 0),
            y=kwargs.get("y", 0)
        )
    elif action_type == ActionType.DELAY:
        return DelayAction(
            id=str(uuid.uuid4()),
            name=name,
            duration=kwargs.get("duration", 1.0)
        )
    else:
        raise ValueError(f"Неизвестный тип действия: {action_type}")
