"""
Модуль для работы с макросами - последовательностями действий.

Поддерживаемые типы действий:
- Клики по координатам (абсолютным, относительным к окну, по распознанной области)
- Задержки
- Условия (переходы по label)
- Циклы
- Проверки состояния
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any


class ActionType(Enum):
    """Типы действий в макросе."""
    
    # Клики
    CLICK_ABSOLUTE = "click_absolute"  # Клик по абсолютным координатам экрана
    CLICK_RELATIVE = "click_relative"  # Клик по относительным координатам к окну
    CLICK_IMAGE = "click_image"  # Клик по распознанной области (image matching)
    
    # Управление потоком
    DELAY = "delay"  # Задержка
    CONDITION = "condition"  # Условие с переходами
    LOOP = "loop"  # Цикл
    GOTO = "goto"  # Безусловный переход к label
    
    # Проверки
    STATE_CHECK = "state_check"  # Проверка состояния области
    
    # Работа с окнами
    NORMALIZE_WINDOW = "normalize_window"  # Применить пресет нормализации
    FOCUS_WINDOW = "focus_window"  # Фокус на окне
    
    # Скриншоты
    TAKE_SCREENSHOT = "take_screenshot"  # Сделать скриншот области


@dataclass
class ClickOffset:
    """Настройки случайного отклонения для кликов."""
    
    enabled: bool = True
    max_offset_x: int = 5  # Максимальное отклонение по X в пикселях
    max_offset_y: int = 5  # Максимальное отклонение по Y в пикселях
    
    def __post_init__(self):
        if self.max_offset_x < 0:
            self.max_offset_x = 0
        if self.max_offset_y < 0:
            self.max_offset_y = 0


@dataclass
class MacroAction:
    """Базовый класс действия макроса."""
    
    id: str  # Уникальный ID действия
    type: ActionType  # Тип действия
    label: str = ""  # Метка для переходов (GOTO)
    description: str = ""  # Описание действия
    enabled: bool = True  # Включено ли действие
    
    # Общие настройки для всех действий
    retry_count: int = 0  # Количество повторений при ошибке
    retry_delay: float = 1.0  # Задержка между повторениями в секундах
    
    def to_dict(self) -> dict[str, Any]:
        """Сериализует действие в словарь."""
        return {
            "id": self.id,
            "type": self.type.value,
            "label": self.label,
            "description": self.description,
            "enabled": self.enabled,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MacroAction":
        """Десериализует действие из словаря."""
        return cls(
            id=data["id"],
            type=ActionType(data["type"]),
            label=data.get("label", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            retry_count=data.get("retry_count", 0),
            retry_delay=data.get("retry_delay", 1.0),
        )


@dataclass
class ClickAbsoluteAction(MacroAction):
    """Действие: клик по абсолютным координатам экрана."""
    
    x: int = 0  # Координата X
    y: int = 0  # Координата Y
    button: str = "left"  # left, right, middle
    double_click: bool = False  # Двойной клик
    offset: ClickOffset = field(default_factory=ClickOffset)  # Настройки отклонения
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({
            "x": self.x,
            "y": self.y,
            "button": self.button,
            "double_click": self.double_click,
            "offset": {
                "enabled": self.offset.enabled,
                "max_offset_x": self.offset.max_offset_x,
                "max_offset_y": self.offset.max_offset_y,
            }
        })
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClickAbsoluteAction":
        action = super(ClickAbsoluteAction, cls).from_dict(data)
        offset_data = data.get("offset", {})
        action.x = data.get("x", 0)
        action.y = data.get("y", 0)
        action.button = data.get("button", "left")
        action.double_click = data.get("double_click", False)
        action.offset = ClickOffset(
            enabled=offset_data.get("enabled", True),
            max_offset_x=offset_data.get("max_offset_x", 5),
            max_offset_y=offset_data.get("max_offset_y", 5),
        )
        return action


@dataclass
class ClickRelativeAction(MacroAction):
    """Действие: клик по относительным координатам к окну процесса."""
    
    preset_id: str = ""  # ID пресета нормализации
    x: int = 0  # Относительная координата X внутри окна
    y: int = 0  # Относительная координата Y внутри окна
    button: str = "left"
    double_click: bool = False
    offset: ClickOffset = field(default_factory=ClickOffset)
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({
            "preset_id": self.preset_id,
            "x": self.x,
            "y": self.y,
            "button": self.button,
            "double_click": self.double_click,
            "offset": {
                "enabled": self.offset.enabled,
                "max_offset_x": self.offset.max_offset_x,
                "max_offset_y": self.offset.max_offset_y,
            }
        })
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClickRelativeAction":
        action = super(ClickRelativeAction, cls).from_dict(data)
        offset_data = data.get("offset", {})
        action.preset_id = data.get("preset_id", "")
        action.x = data.get("x", 0)
        action.y = data.get("y", 0)
        action.button = data.get("button", "left")
        action.double_click = data.get("double_click", False)
        action.offset = ClickOffset(
            enabled=offset_data.get("enabled", True),
            max_offset_x=offset_data.get("max_offset_x", 5),
            max_offset_y=offset_data.get("max_offset_y", 5),
        )
        return action


@dataclass
class ClickImageAction(MacroAction):
    """Действие: клик по распознанной области (image matching)."""
    
    preset_image_path: str = ""  # Путь к изображению для поиска
    preset_id: str = ""  # ID пресета скриншота
    confidence_threshold: float = 0.8  # Порог уверенности
    button: str = "left"
    double_click: bool = False
    offset: ClickOffset = field(default_factory=ClickOffset)
    click_position: str = "center"  # center, top_left, random
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({
            "preset_image_path": self.preset_image_path,
            "preset_id": self.preset_id,
            "confidence_threshold": self.confidence_threshold,
            "button": self.button,
            "double_click": self.double_click,
            "offset": {
                "enabled": self.offset.enabled,
                "max_offset_x": self.offset.max_offset_x,
                "max_offset_y": self.offset.max_offset_y,
            },
            "click_position": self.click_position,
        })
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClickImageAction":
        action = super(ClickImageAction, cls).from_dict(data)
        offset_data = data.get("offset", {})
        action.preset_image_path = data.get("preset_image_path", "")
        action.preset_id = data.get("preset_id", "")
        action.confidence_threshold = data.get("confidence_threshold", 0.8)
        action.button = data.get("button", "left")
        action.double_click = data.get("double_click", False)
        action.offset = ClickOffset(
            enabled=offset_data.get("enabled", True),
            max_offset_x=offset_data.get("max_offset_x", 5),
            max_offset_y=offset_data.get("max_offset_y", 5),
        )
        action.click_position = data.get("click_position", "center")
        return action


@dataclass
class DelayAction(MacroAction):
    """Действие: задержка выполнения."""
    
    duration: float = 1.0  # Длительность задержки в секундах
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result["duration"] = self.duration
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DelayAction":
        action = super(DelayAction, cls).from_dict(data)
        action.duration = data.get("duration", 1.0)
        return action


@dataclass
class ConditionBranch:
    """Ветка условия (true/false)."""
    
    action: str = "continue"  # continue, goto, break
    target_label: str = ""  # Label для перехода (если action == goto)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "target_label": self.target_label,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConditionBranch":
        return cls(
            action=data.get("action", "continue"),
            target_label=data.get("target_label", ""),
        )


@dataclass
class ConditionAction(MacroAction):
    """Действие: условие с переходами."""
    
    condition_type: str = "image_exists"  # image_exists, image_not_exists, color_at_pixel
    # Для image_exists/image_not_exists
    preset_image_path: str = ""
    preset_id: str = ""
    confidence_threshold: float = 0.8
    # Для color_at_pixel
    check_x: int = 0
    check_y: int = 0
    expected_color: tuple[int, int, int] = (0, 0, 0)
    color_tolerance: int = 10
    
    # Ветки выполнения
    on_true: ConditionBranch = field(default_factory=lambda: ConditionBranch())
    on_false: ConditionBranch = field(default_factory=lambda: ConditionBranch())
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({
            "condition_type": self.condition_type,
            "preset_image_path": self.preset_image_path,
            "preset_id": self.preset_id,
            "confidence_threshold": self.confidence_threshold,
            "check_x": self.check_x,
            "check_y": self.check_y,
            "expected_color": list(self.expected_color),
            "color_tolerance": self.color_tolerance,
            "on_true": self.on_true.to_dict(),
            "on_false": self.on_false.to_dict(),
        })
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConditionAction":
        action = super(ConditionAction, cls).from_dict(data)
        action.condition_type = data.get("condition_type", "image_exists")
        action.preset_image_path = data.get("preset_image_path", "")
        action.preset_id = data.get("preset_id", "")
        action.confidence_threshold = data.get("confidence_threshold", 0.8)
        action.check_x = data.get("check_x", 0)
        action.check_y = data.get("check_y", 0)
        action.expected_color = tuple(data.get("expected_color", [0, 0, 0]))
        action.color_tolerance = data.get("color_tolerance", 10)
        action.on_true = ConditionBranch.from_dict(data.get("on_true", {}))
        action.on_false = ConditionBranch.from_dict(data.get("on_false", {}))
        return action


@dataclass
class LoopAction(MacroAction):
    """Действие: цикл."""
    
    loop_type: str = "count"  # count, while_image_exists, while_image_not_exists
    # Для count
    iterations: int = 1
    # Для while_*
    preset_image_path: str = ""
    preset_id: str = ""
    confidence_threshold: float = 0.8
    max_iterations: int = 100  # Защита от бесконечных циклов
    
    # Действия внутри цикла будут храниться в макросе между этим действием и LoopEnd
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({
            "loop_type": self.loop_type,
            "iterations": self.iterations,
            "preset_image_path": self.preset_image_path,
            "preset_id": self.preset_id,
            "confidence_threshold": self.confidence_threshold,
            "max_iterations": self.max_iterations,
        })
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LoopAction":
        action = super(LoopAction, cls).from_dict(data)
        action.loop_type = data.get("loop_type", "count")
        action.iterations = data.get("iterations", 1)
        action.preset_image_path = data.get("preset_image_path", "")
        action.preset_id = data.get("preset_id", "")
        action.confidence_threshold = data.get("confidence_threshold", 0.8)
        action.max_iterations = data.get("max_iterations", 100)
        return action


@dataclass
class GotoAction(MacroAction):
    """Действие: безусловный переход к label."""
    
    target_label: str = ""  # Label для перехода
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result["target_label"] = self.target_label
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GotoAction":
        action = super(GotoAction, cls).from_dict(data)
        action.target_label = data.get("target_label", "")
        return action


@dataclass
class StateCheckAction(MacroAction):
    """
    Действие: проверка состояния области.
    
    Делает скриншот указанной области, ждет, делает второй скриншот,
    сравнивает их и выполняет разные действия в зависимости от результата.
    """
    
    # Область для проверки
    area_type: str = "absolute"  # absolute, relative, image
    area_x: int = 0
    area_y: int = 0
    area_width: int = 100
    area_height: int = 100
    preset_id: str = ""  # Для relative/area
    
    # Настройки проверки
    wait_duration: float = 1.0  # Время ожидания между снимками в секундах
    comparison_threshold: float = 0.95  # Порог схожести изображений (0-1)
    
    # Повторы для стабильности
    unchanged_required: int = 1  # Сколько раз состояние должно повториться чтобы считать что не изменилось
    changed_allowed: int = 1  # Сколько раз состояние может измениться прежде чем считать что изменилось
    
    # Действия при результате
    on_unchanged: ConditionBranch = field(default_factory=lambda: ConditionBranch())
    on_changed: ConditionBranch = field(default_factory=lambda: ConditionBranch())
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({
            "area_type": self.area_type,
            "area_x": self.area_x,
            "area_y": self.area_y,
            "area_width": self.area_width,
            "area_height": self.area_height,
            "preset_id": self.preset_id,
            "wait_duration": self.wait_duration,
            "comparison_threshold": self.comparison_threshold,
            "unchanged_required": self.unchanged_required,
            "changed_allowed": self.changed_allowed,
            "on_unchanged": self.on_unchanged.to_dict(),
            "on_changed": self.on_changed.to_dict(),
        })
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StateCheckAction":
        action = super(StateCheckAction, cls).from_dict(data)
        action.area_type = data.get("area_type", "absolute")
        action.area_x = data.get("area_x", 0)
        action.area_y = data.get("area_y", 0)
        action.area_width = data.get("area_width", 100)
        action.area_height = data.get("area_height", 100)
        action.preset_id = data.get("preset_id", "")
        action.wait_duration = data.get("wait_duration", 1.0)
        action.comparison_threshold = data.get("comparison_threshold", 0.95)
        action.unchanged_required = data.get("unchanged_required", 1)
        action.changed_allowed = data.get("changed_allowed", 1)
        action.on_unchanged = ConditionBranch.from_dict(data.get("on_unchanged", {}))
        action.on_changed = ConditionBranch.from_dict(data.get("on_changed", {}))
        return action


@dataclass
class NormalizeWindowAction(MacroAction):
    """Действие: применить пресет нормализации к окну."""
    
    preset_id: str = ""  # ID пресета нормализации
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result["preset_id"] = self.preset_id
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NormalizeWindowAction":
        action = super(NormalizeWindowAction, cls).from_dict(data)
        action.preset_id = data.get("preset_id", "")
        return action


@dataclass
class FocusWindowAction(MacroAction):
    """Действие: фокус на окне."""
    
    preset_id: str = ""  # ID пресета нормализации для поиска окна
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result["preset_id"] = self.preset_id
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FocusWindowAction":
        action = super(FocusWindowAction, cls).from_dict(data)
        action.preset_id = data.get("preset_id", "")
        return action


@dataclass
class TakeScreenshotAction(MacroAction):
    """Действие: сделать скриншот области."""
    
    area_type: str = "absolute"  # absolute, relative
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 100
    preset_id: str = ""  # Для relative
    output_path: str = ""  # Путь сохранения (пустой = автогенерация)
    screenshot_id: str = ""  # ID скриншота (пустой = автогенерация)
    
    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({
            "area_type": self.area_type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "preset_id": self.preset_id,
            "output_path": self.output_path,
            "screenshot_id": self.screenshot_id,
        })
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TakeScreenshotAction":
        action = super(TakeScreenshotAction, cls).from_dict(data)
        action.area_type = data.get("area_type", "absolute")
        action.x = data.get("x", 0)
        action.y = data.get("y", 0)
        action.width = data.get("width", 100)
        action.height = data.get("height", 100)
        action.preset_id = data.get("preset_id", "")
        action.output_path = data.get("output_path", "")
        action.screenshot_id = data.get("screenshot_id", "")
        return action


# Тип для любого действия
MacroActionType = (
    ClickAbsoluteAction |
    ClickRelativeAction |
    ClickImageAction |
    DelayAction |
    ConditionAction |
    LoopAction |
    GotoAction |
    StateCheckAction |
    NormalizeWindowAction |
    FocusWindowAction |
    TakeScreenshotAction
)


def action_from_dict(data: dict[str, Any]) -> MacroActionType:
    """Фабричный метод для создания действия из словаря."""
    action_type = ActionType(data["type"])
    
    match action_type:
        case ActionType.CLICK_ABSOLUTE:
            return ClickAbsoluteAction.from_dict(data)
        case ActionType.CLICK_RELATIVE:
            return ClickRelativeAction.from_dict(data)
        case ActionType.CLICK_IMAGE:
            return ClickImageAction.from_dict(data)
        case ActionType.DELAY:
            return DelayAction.from_dict(data)
        case ActionType.CONDITION:
            return ConditionAction.from_dict(data)
        case ActionType.LOOP:
            return LoopAction.from_dict(data)
        case ActionType.GOTO:
            return GotoAction.from_dict(data)
        case ActionType.STATE_CHECK:
            return StateCheckAction.from_dict(data)
        case ActionType.NORMALIZE_WINDOW:
            return NormalizeWindowAction.from_dict(data)
        case ActionType.FOCUS_WINDOW:
            return FocusWindowAction.from_dict(data)
        case ActionType.TAKE_SCREENSHOT:
            return TakeScreenshotAction.from_dict(data)
        case _:
            raise ValueError(f"Неизвестный тип действия: {action_type}")
