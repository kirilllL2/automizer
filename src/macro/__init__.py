"""
Модуль бизнес-логики для работы с макросами на основе Python-файлов.
Макросы определяются как Python-файлы в папке macros/.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import importlib.util
import sys
import time
import threading


# Импортируем действия из модуля actions для удобного использования в макросах
from src.macro.actions import (
    Region,
    click,
    click_in_region,
    find_region,
    find_all_regions,
    wait_for_region,
    get_screen_size,
    create_region_from_center,
    focus_window,
    click_in_window_region,
    find_window_by_process,
)


@dataclass
class MacroInfo:
    """Информация о макросе."""
    id: str  # имя файла без .py
    name: str
    description: str = ""
    file_path: Path = field(default_factory=Path)
    is_running: bool = False
    thread: Optional[threading.Thread] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_running": self.is_running
        }


class MacroStorage:
    """Хранилище макросов, загружаемых из Python-файлов."""
    
    def __init__(self, macros_dir: Optional[Path] = None):
        if macros_dir is None:
            macros_dir = Path(__file__).parent / "macros"
        self.macros_dir = macros_dir
        self.macros_dir.mkdir(parents=True, exist_ok=True)
        self.macros: Dict[str, MacroInfo] = {}
        self._module_cache: Dict[str, Any] = {}
        self._load_macros()
    
    def _load_macros(self):
        """Загружает макросы из Python-файлов в директории macros/."""
        self.macros.clear()
        self._module_cache.clear()
        
        for file_path in self.macros_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            macro_id = file_path.stem
            try:
                # Загружаем модуль
                spec = importlib.util.spec_from_file_location(macro_id, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[macro_id] = module
                    spec.loader.exec_module(module)
                    
                    # Получаем метаданные из модуля
                    name = getattr(module, "NAME", macro_id)
                    description = getattr(module, "DESCRIPTION", "")
                    
                    macro_info = MacroInfo(
                        id=macro_id,
                        name=name,
                        description=description,
                        file_path=file_path
                    )
                    self.macros[macro_id] = macro_info
                    self._module_cache[macro_id] = module
                    
            except Exception as e:
                print(f"[MacroStorage] Ошибка загрузки макроса {file_path.name}: {e}")
        
        print(f"[MacroStorage] Загружено {len(self.macros)} макросов")
    
    def reload_macros(self):
        """Перезагружает список макросов."""
        self._load_macros()
    
    def get_macro(self, macro_id: str) -> Optional[MacroInfo]:
        """Получает информацию о макросе по ID."""
        return self.macros.get(macro_id)
    
    def list_macros(self) -> List[MacroInfo]:
        """Возвращает список всех макросов."""
        return list(self.macros.values())
    
    def execute_macro(self, macro_id: str) -> bool:
        """Выполняет макрос в отдельном потоке."""
        macro_info = self.get_macro(macro_id)
        if not macro_info:
            return False
        
        if macro_info.is_running:
            print(f"[MacroStorage] Макрос '{macro_info.name}' уже выполняется")
            return False
        
        module = self._module_cache.get(macro_id)
        if not module:
            print(f"[MacroStorage] Модуль для макроса '{macro_id}' не найден")
            return False
        
        # Проверяем наличие функции run
        if not hasattr(module, "run") or not callable(module.run):
            print(f"[MacroStorage] В макросе '{macro_id}' нет функции run()")
            return False
        
        def run_macro():
            macro_info.is_running = True
            try:
                print(f"[MacroStorage] Запуск макроса '{macro_info.name}'")
                module.run()
                print(f"[MacroStorage] Макрос '{macro_info.name}' завершен")
            except Exception as e:
                print(f"[MacroStorage] Ошибка выполнения макроса '{macro_info.name}': {e}")
            finally:
                macro_info.is_running = False
        
        macro_info.thread = threading.Thread(target=run_macro, daemon=True)
        macro_info.thread.start()
        return True
    
    def stop_macro(self, macro_id: str) -> bool:
        """Останавливает выполнение макроса (помечает как остановленный)."""
        macro_info = self.get_macro(macro_id)
        if not macro_info or not macro_info.is_running:
            return False
        
        # Фактическая остановка зависит от реализации макроса
        # Здесь мы просто помечаем что он больше не выполняется
        macro_info.is_running = False
        print(f"[MacroStorage] Макрос '{macro_info.name}' остановлен")
        return True
    
    def is_macro_running(self, macro_id: str) -> bool:
        """Проверяет, выполняется ли макрос."""
        macro_info = self.get_macro(macro_id)
        return macro_info.is_running if macro_info else False


# Вспомогательные функции для использования в макросах
# Эти функции теперь импортируются из src.macro.actions для удобства
# Для обратной совместимости оставляем алиасы

def delay(seconds: float):
    """Выполняет задержку на указанное количество секунд."""
    print(f"[Action] Задержка на {seconds} сек.")
    time.sleep(seconds)


def wait_for(condition: Callable[[], bool], timeout: float = 10.0, interval: float = 0.1) -> bool:
    """Ждет выполнения условия до истечения таймаута."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    return False
