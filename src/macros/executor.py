"""
Исполнитель макросов - выполняет действия макроса.
"""

import random
import time
from pathlib import Path
from typing import Optional, Callable, Any

from src.macros import (
    Macro,
    MacroAction,
    ActionType,
    ClickAbsoluteAction,
    ClickRelativeAction,
    ClickImageAction,
    DelayAction,
    ConditionAction,
    LoopAction,
    GotoAction,
    StateCheckAction,
    NormalizeWindowAction,
    FocusWindowAction,
    TakeScreenshotAction,
    ConditionBranch,
)
from src.window_manager import WindowManager
from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.storage import PresetStorage
from src.screenshot import ScreenshotManager
from src.cv import CVMatcher


class ExecutionState:
    """Состояние выполнения макроса."""
    
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


class MacroExecutionError(Exception):
    """Ошибка выполнения макроса."""
    pass


class MacroExecutor:
    """Исполнитель макросов."""
    
    def __init__(
        self,
        window_manager: Optional[WindowManager] = None,
        normalizer: Optional[ProcessNormalizer] = None,
        preset_storage: Optional[PresetStorage] = None,
        screenshot_manager: Optional[ScreenshotManager] = None,
        cv_matcher: Optional[CVMatcher] = None,
    ):
        self.window_manager = window_manager or WindowManager()
        self.normalizer = normalizer or ProcessNormalizer(self.window_manager)
        self.preset_storage = preset_storage or PresetStorage()
        self.screenshot_manager = screenshot_manager or ScreenshotManager()
        self.cv_matcher = cv_matcher or CVMatcher()
        
        self._state = ExecutionState.STOPPED
        self._current_macro: Optional[Macro] = None
        self._current_action_index = 0
        self._label_index: dict[str, int] = {}
        self._loop_stack: list[dict[str, Any]] = []
        
        # Callbacks
        self.on_action_start: Optional[Callable[[MacroAction, int], None]] = None
        self.on_action_complete: Optional[Callable[[MacroAction, int], None]] = None
        self.on_action_error: Optional[Callable[[MacroAction, int, Exception], None]] = None
        self.on_macro_complete: Optional[Callable[[Macro], None]] = None
        self.on_macro_error: Optional[Callable[[Macro, Exception], None]] = None
    
    @property
    def state(self) -> str:
        return self._state
    
    @property
    def current_action_index(self) -> int:
        return self._current_action_index
    
    def _build_label_index(self, macro: Macro) -> dict[str, int]:
        """Строит индекс label -> индекс действия."""
        label_index = {}
        for i, action in enumerate(macro.actions):
            if action.label:
                label_index[action.label] = i
        return label_index
    
    def _apply_offset(self, x: int, y: int, offset_enabled: bool, max_offset_x: int, max_offset_y: int) -> tuple[int, int]:
        """Применяет случайное отклонение к координатам."""
        if not offset_enabled:
            return x, y
        
        dx = random.randint(-max_offset_x, max_offset_x)
        dy = random.randint(-max_offset_y, max_offset_y)
        return x + dx, y + dy
    
    def _click(self, x: int, y: int, button: str = "left", double_click: bool = False) -> bool:
        """Выполняет клик по координатам."""
        try:
            import pyautogui
            pyautogui.click(x=x, y=y, button=button, clicks=2 if double_click else 1)
            return True
        except ImportError:
            raise MacroExecutionError("Требуется библиотека pyautogui для выполнения кликов")
        except Exception as e:
            raise MacroExecutionError(f"Ошибка при клике: {e}")
    
    def _find_window_by_preset(self, preset_id: str) -> Optional[int]:
        """Находит окно по пресету нормализации."""
        preset = self.preset_storage.get_preset(preset_id)
        if not preset:
            return None
        
        window = self.normalizer.find_window_by_process(preset.process_name)
        if window:
            return window.window_id
        return None
    
    def _compare_images(self, image1_path: Path, image2_path: Path, threshold: float) -> bool:
        """Сравнивает два изображения на схожесть."""
        try:
            import cv2
            import numpy as np
            
            img1 = cv2.imread(str(image1_path))
            img2 = cv2.imread(str(image2_path))
            
            if img1 is None or img2 is None:
                return False
            
            # Изменяем размер до одинакового
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Вычисляем корреляцию
            correlation = np.corrcoef(img1.flatten(), img2.flatten())[0, 1]
            return correlation >= threshold
            
        except ImportError:
            raise MacroExecutionError("Требуется OpenCV и NumPy для сравнения изображений")
        except Exception as e:
            raise MacroExecutionError(f"Ошибка при сравнении изображений: {e}")
    
    def _execute_condition_branch(self, branch: ConditionBranch) -> Optional[int]:
        """
        Выполняет ветку условия.
        Возвращает новый индекс действия или None для продолжения.
        """
        if branch.action == "goto":
            if branch.target_label in self._label_index:
                return self._label_index[branch.target_label]
            else:
                raise MacroExecutionError(f"Label '{branch.target_label}' не найден")
        elif branch.action == "break":
            # Прерываем цикл
            if self._loop_stack:
                self._loop_stack.pop()
            return None
        # continue - продолжаем выполнение
        return None
    
    def _execute_action(self, action: MacroAction, index: int) -> Optional[int]:
        """
        Выполняет одно действие.
        Возвращает следующий индекс действия или None для продолжения по порядку.
        """
        if not action.enabled:
            return None
        
        # Обработка retry
        retries = action.retry_count
        last_error: Optional[Exception] = None
        
        while retries >= 0:
            try:
                if self.on_action_start:
                    self.on_action_start(action, index)
                
                next_index = self._do_execute_action(action, index)
                
                if self.on_action_complete:
                    self.on_action_complete(action, index)
                
                return next_index
                
            except Exception as e:
                last_error = e
                if self.on_action_error:
                    self.on_action_error(action, index, e)
                
                if retries > 0:
                    time.sleep(action.retry_delay)
                    retries -= 1
                else:
                    raise last_error
        
        return None
    
    def _do_execute_action(self, action: MacroAction, index: int) -> Optional[int]:
        """Выполняет конкретное действие."""
        
        match action:
            case ClickAbsoluteAction():
                x, y = self._apply_offset(
                    action.x, action.y,
                    action.offset.enabled,
                    action.offset.max_offset_x,
                    action.offset.max_offset_y,
                )
                self._click(x, y, action.button, action.double_click)
                
            case ClickRelativeAction():
                window_id = self._find_window_by_preset(action.preset_id)
                if not window_id:
                    raise MacroExecutionError(f"Окно для пресета '{action.preset_id}' не найдено")
                
                # Получаем позицию окна
                window_info = None
                for w in self.window_manager.get_windows():
                    if w.window_id == window_id:
                        window_info = w
                        break
                
                if not window_info:
                    raise MacroExecutionError("Не удалось получить информацию об окне")
                
                x, y = self._apply_offset(
                    action.x, action.y,
                    action.offset.enabled,
                    action.offset.max_offset_x,
                    action.offset.max_offset_y,
                )
                
                # Конвертируем относительные координаты в абсолютные
                abs_x = window_info.x + x
                abs_y = window_info.y + y
                
                self._click(abs_x, abs_y, action.button, action.double_click)
                
            case ClickImageAction():
                result = self.cv_matcher.find_match(
                    preset_image_path=action.preset_image_path,
                    preset_id=action.preset_id,
                    preset_name="",
                    confidence_threshold=action.confidence_threshold,
                )
                
                if not result:
                    raise MacroExecutionError("Изображение не найдено на экране")
                
                # Определяем точку клика
                if action.click_position == "center":
                    x = result.x + result.width // 2
                    y = result.y + result.height // 2
                elif action.click_position == "top_left":
                    x = result.x
                    y = result.y
                else:  # random
                    x = result.x + random.randint(0, result.width)
                    y = result.y + random.randint(0, result.height)
                
                # Применяем отклонение
                x, y = self._apply_offset(
                    x, y,
                    action.offset.enabled,
                    action.offset.max_offset_x,
                    action.offset.max_offset_y,
                )
                
                self._click(x, y, action.button, action.double_click)
                
            case DelayAction():
                time.sleep(action.duration)
                
            case ConditionAction():
                condition_met = False
                
                if action.condition_type == "image_exists":
                    result = self.cv_matcher.find_match(
                        preset_image_path=action.preset_image_path,
                        preset_id=action.preset_id,
                        preset_name="",
                        confidence_threshold=action.confidence_threshold,
                    )
                    condition_met = result is not None
                    
                elif action.condition_type == "image_not_exists":
                    result = self.cv_matcher.find_match(
                        preset_image_path=action.preset_image_path,
                        preset_id=action.preset_id,
                        preset_name="",
                        confidence_threshold=action.confidence_threshold,
                    )
                    condition_met = result is None
                    
                elif action.condition_type == "color_at_pixel":
                    try:
                        import pyautogui
                        pixel_color = pyautogui.pixel(action.check_x, action.check_y)
                        
                        # Сравниваем с допуском
                        r_diff = abs(pixel_color[0] - action.expected_color[0])
                        g_diff = abs(pixel_color[1] - action.expected_color[1])
                        b_diff = abs(pixel_color[2] - action.expected_color[2])
                        
                        condition_met = (
                            r_diff <= action.color_tolerance and
                            g_diff <= action.color_tolerance and
                            b_diff <= action.color_tolerance
                        )
                    except ImportError:
                        raise MacroExecutionError("Требуется pyautogui для проверки цвета пикселя")
                
                # Выполняем соответствующую ветку
                if condition_met:
                    return self._execute_condition_branch(action.on_true)
                else:
                    return self._execute_condition_branch(action.on_false)
                
            case LoopAction():
                # Инициализация цикла
                loop_data = {
                    "start_index": index,
                    "iterations": action.iterations,
                    "current_iteration": 0,
                    "loop_type": action.loop_type,
                    "preset_image_path": action.preset_image_path,
                    "preset_id": action.preset_id,
                    "confidence_threshold": action.confidence_threshold,
                    "max_iterations": action.max_iterations,
                }
                self._loop_stack.append(loop_data)
                # Продолжаем к следующему действию (тело цикла)
                
            case GotoAction():
                if action.target_label in self._label_index:
                    return self._label_index[action.target_label]
                else:
                    raise MacroExecutionError(f"Label '{action.target_label}' не найден")
                
            case StateCheckAction():
                # Определяем область для скриншота
                area_x, area_y, area_w, area_h = self._get_check_area(action)
                
                unchanged_count = 0
                changed_count = 0
                
                # Выполняем проверки
                for _ in range(max(action.unchanged_required, action.changed_allowed)):
                    # Первый скриншот
                    screenshot1 = self.screenshot_manager.capture(
                        x=area_x,
                        y=area_y,
                        width=area_w,
                        height=area_h,
                        screenshot_id=f"state_check_1_{time.time()}",
                    )
                    
                    # Ждем
                    time.sleep(action.wait_duration)
                    
                    # Второй скриншот
                    screenshot2 = self.screenshot_manager.capture(
                        x=area_x,
                        y=area_y,
                        width=area_w,
                        height=area_h,
                        screenshot_id=f"state_check_2_{time.time()}",
                    )
                    
                    # Сравниваем
                    images_equal = self._compare_images(
                        screenshot1.path,
                        screenshot2.path,
                        action.comparison_threshold,
                    )
                    
                    if images_equal:
                        unchanged_count += 1
                        if unchanged_count >= action.unchanged_required:
                            # Считаем что состояние не изменилось
                            return self._execute_condition_branch(action.on_unchanged)
                    else:
                        changed_count += 1
                        if changed_count >= action.changed_allowed:
                            # Считаем что состояние изменилось
                            return self._execute_condition_branch(action.on_changed)
                
                # Если не достигли порога ни для одного варианта
                # По умолчанию считаем что не изменилось
                return self._execute_condition_branch(action.on_unchanged)
                
            case NormalizeWindowAction():
                preset = self.preset_storage.get_preset(action.preset_id)
                if not preset:
                    raise MacroExecutionError(f"Пресет '{action.preset_id}' не найден")
                
                success = self.normalizer.apply_preset(preset)
                if not success:
                    raise MacroExecutionError("Не удалось применить пресет нормализации")
                
            case FocusWindowAction():
                window_id = self._find_window_by_preset(action.preset_id)
                if not window_id:
                    raise MacroExecutionError(f"Окно для пресета '{action.preset_id}' не найдено")
                
                success = self.window_manager.focus_window(window_id)
                if not success:
                    raise MacroExecutionError("Не удалось сфокусировать окно")
                
            case TakeScreenshotAction():
                if action.area_type == "relative":
                    window_id = self._find_window_by_preset(action.preset_id)
                    if not window_id:
                        raise MacroExecutionError(f"Окно для пресета '{action.preset_id}' не найдено")
                    
                    window_info = None
                    for w in self.window_manager.get_windows():
                        if w.window_id == window_id:
                            window_info = w
                            break
                    
                    if not window_info:
                        raise MacroExecutionError("Не удалось получить информацию об окне")
                    
                    x = window_info.x + action.x
                    y = window_info.y + action.y
                else:
                    x = action.x
                    y = action.y
                
                self.screenshot_manager.capture(
                    x=x,
                    y=y,
                    width=action.width,
                    height=action.height,
                    screenshot_id=action.screenshot_id or None,
                    output_path=action.output_path or None,
                )
                
            case _:
                raise MacroExecutionError(f"Неизвестный тип действия: {action.type}")
        
        return None
    
    def _get_check_area(self, action: StateCheckAction) -> tuple[int, int, int, int]:
        """Получает координаты области для проверки состояния."""
        if action.area_type == "absolute":
            return action.area_x, action.area_y, action.area_width, action.area_height
        
        elif action.area_type == "relative":
            window_id = self._find_window_by_preset(action.preset_id)
            if not window_id:
                raise MacroExecutionError(f"Окно для пресета '{action.preset_id}' не найдено")
            
            window_info = None
            for w in self.window_manager.get_windows():
                if w.window_id == window_id:
                    window_info = w
                    break
            
            if not window_info:
                raise MacroExecutionError("Не удалось получить информацию об окне")
            
            return (
                window_info.x + action.area_x,
                window_info.y + action.area_y,
                action.area_width,
                action.area_height,
            )
        
        elif action.area_type == "image":
            result = self.cv_matcher.find_match(
                preset_image_path="",
                preset_id=action.preset_id,
                preset_name="",
                confidence_threshold=0.8,
            )
            if not result:
                raise MacroExecutionError(f"Изображение '{action.preset_id}' не найдено")
            
            return result.x, result.y, result.width, result.height
        
        raise MacroExecutionError(f"Неизвестный тип области: {action.area_type}")
    
    def execute(self, macro: Macro) -> bool:
        """
        Выполняет макрос.
        
        Returns:
            True если макрос выполнен успешно, False если произошла ошибка.
        """
        self._state = ExecutionState.RUNNING
        self._current_macro = macro
        self._current_action_index = 0
        self._label_index = self._build_label_index(macro)
        self._loop_stack = []
        
        try:
            while self._current_action_index < len(macro.actions):
                if self._state == ExecutionState.STOPPED:
                    return False
                
                action = macro.actions[self._current_action_index]
                
                # Проверяем если мы внутри цикла
                if self._loop_stack:
                    loop_data = self._loop_stack[-1]
                    
                    # Для циклов по счетчику
                    if loop_data["loop_type"] == "count":
                        if self._current_action_index > loop_data["start_index"]:
                            # Это не первое действие цикла
                            if self._current_action_index == loop_data.get("end_index"):
                                # Конец цикла
                                loop_data["current_iteration"] += 1
                                
                                if loop_data["current_iteration"] >= loop_data["iterations"]:
                                    # Цикл завершен
                                    self._loop_stack.pop()
                                else:
                                    # Повторяем цикл
                                    self._current_action_index = loop_data["start_index"] + 1
                                    continue
                
                next_index = self._execute_action(action, self._current_action_index)
                
                if next_index is not None:
                    self._current_action_index = next_index
                else:
                    self._current_action_index += 1
            
            self._state = ExecutionState.COMPLETED
            
            if self.on_macro_complete:
                self.on_macro_complete(macro)
            
            return True
            
        except Exception as e:
            self._state = ExecutionState.ERROR
            
            if self.on_macro_error:
                self.on_macro_error(macro, e)
            
            return False
    
    def stop(self) -> None:
        """Останавливает выполнение макроса."""
        self._state = ExecutionState.STOPPED
    
    def pause(self) -> None:
        """Ставит макрос на паузу."""
        self._state = ExecutionState.PAUSED
    
    def resume(self) -> None:
        """Возобновляет выполнение макроса."""
        if self._state == ExecutionState.PAUSED:
            self._state = ExecutionState.RUNNING
