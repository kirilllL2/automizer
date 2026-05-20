"""
Консольный интерфейс для управления окнами.

Предоставляет простой CLI для тестирования функциональности WindowManager.
"""

import sys
from typing import Optional

from src.window_manager import WindowInfo, WindowManager
from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.storage import PresetStorage
from src.screenshot import ScreenshotManager, ScreenshotInfo
from src.screenshot.presets import ScreenshotPresetStorage, ScreenshotPreset


def print_windows(windows: list[WindowInfo]) -> None:
    """Выводит список окон в виде таблицы."""
    if not windows:
        print("Нет видимых окон.")
        return

    print("\n" + "=" * 80)
    print(f"{'ID':<12} {'PID':<8} {'X':<6} {'Y':<6} {'W':<6} {'H':<6} {'Заголовок'}")
    print("=" * 80)

    for win in windows:
        pid_str = str(win.pid) if win.pid else "N/A"
        title = win.title[:45] + "..." if len(win.title) > 45 else win.title
        print(
            f"{win.window_id:<12} {pid_str:<8} {win.x:<6} {win.y:<6} "
            f"{win.width:<6} {win.height:<6} {title}"
        )

    print("=" * 80)
    print(f"Всего окон: {len(windows)}\n")


def print_presets(presets: list[NormalizationPreset]) -> None:
    """Выводит список пресетов в виде таблицы."""
    if not presets:
        print("Нет сохраненных пресетов.")
        return

    print("\n" + "=" * 80)
    print(f"{'ID':<15} {'Имя':<20} {'Процесс':<15} {'Позиция':<20} {'Размер'}")
    print("=" * 80)

    for preset in presets:
        position = f"({preset.x}, {preset.y})"
        size = f"{preset.width}x{preset.height}"
        print(f"{preset.id:<15} {preset.name:<20} {preset.process_name:<15} {position:<20} {size}")

    print("=" * 80)
    print(f"Всего пресетов: {len(presets)}\n")


def print_screenshots(screenshots: list) -> None:
    """Выводит список скриншотов в виде таблицы."""
    if not screenshots:
        print("Нет сохраненных скриншотов.")
        return

    print("\n" + "=" * 100)
    print(f"{'ID':<25} {'Путь':<35} {'Позиция':<15} {'Размер':<12} {'Дата создания'}")
    print("=" * 100)

    for ss in screenshots:
        path_str = str(ss.path)[-32:]  # Последние 32 символа пути
        position = f"({ss.x}, {ss.y})"
        size = f"{ss.width}x{ss.height}"
        date_str = ss.created_at.strftime("%Y-%m-%d %H:%M")
        print(f"{ss.id:<25} {path_str:<35} {position:<15} {size:<12} {date_str}")

    print("=" * 100)
    print(f"Всего скриншотов: {len(screenshots)}\n")


def print_screenshot_presets(presets: list[ScreenshotPreset]) -> None:
    """Выводит список пресетов скриншотов в виде таблицы."""
    if not presets:
        print("Нет сохраненных пресетов скриншотов.")
        return

    print("\n" + "=" * 120)
    print(f"{'ID':<20} {'Имя':<25} {'Путь':<30} {'Процесс':<15} {'Позиция':<15} {'Размер'}")
    print("=" * 120)

    for preset in presets:
        position = f"({preset.x}, {preset.y})"
        size = f"{preset.width}x{preset.height}"
        print(f"{preset.id:<20} {preset.name:<25} {preset.screenshot_path:<30} {preset.process_preset_id:<15} {position:<15} {size}")

    print("=" * 120)
    print(f"Всего пресетов скриншотов: {len(presets)}\n")


def print_help() -> None:
    """Выводит справку по командам."""
    print("""
Доступные команды:

Управление окнами:
  list, l              - Показать список всех окон
  move <id> <x> <y>    - Переместить окно с указанным ID в координаты (x, y)
  resize <id> <w> <h>  - Изменить размер окна на (width x height)
  focus <id>           - Сфокусироваться на окне
  set <id> [x] [y] [w] [h] - Установить позицию и/или размер 
                           (используйте '-' для пропуска параметра)
  normalize <id> <x> <y> <w> <h> - Нормализовать окно (позиция + размер)

Управление пресетами нормализации:
  presets, p           - Показать все сохраненные пресеты нормализации
  preset_search <q>    - Поиск пресетов нормализации по запросу
  preset_apply <id>    - Применить пресет нормализации к окну
  preset_add <id> <name> <process> <x> <y> <w> <h> [description] - Добавить пресет нормализации
  preset_remove <id>   - Удалить пресет нормализации
  preset_edit <id> [--name=N] [--process=P] [--x=X] [--y=Y] [--w=W] [--h=H]
                       - Редактировать пресет нормализации

Управление пресетами скриншотов:
  screenshot_presets, sp          - Показать все пресеты скриншотов
  screenshot_preset_search <q>    - Поиск пресетов скриншотов по запросу
  screenshot_preset_add <id> <name> <path> <process_preset_id> <x> <y> <w> <h> [desc]
                                  - Добавить пресет скриншота
  screenshot_preset_remove <id>   - Удалить пресет скриншота
  screenshot_preset_capture <id> [screenshot_id] - Сделать скриншот по пресету
  quick_capture <process_preset_id> <screenshot_preset_id> [screenshot_id]
                                  - Быстрый захват: нормализовать окно + сделать скриншот

Управление скриншотами:
  screenshots, ss      - Показать все сохраненные скриншоты
  screenshot <x> <y> <w> <h> [id] [desc] - Сделать скриншот области
  screenshot_preview <x> <y> <w> <h> [id] [desc] - Скриншот с превью (красный квадрат)
  screenshot_remove <id> - Удалить скриншот
  screenshot_search <q> - Поиск скриншотов по запросу

Поиск окон:
  search <query>       - Поиск окон по заголовку
  refresh, r           - Обновить список окон

Другие:
  help, h              - Показать эту справку
  quit, q              - Выйти из программы

Примеры:
  move 12345 100 200   - Переместить окно 12345 в точку (100, 200)
  normalize 12345 0 0 960 1080 - Нормализовать окно на левую половину экрана
  preset_add browser_left "Browser Left" Chrome 0 0 960 1080 "Браузер слева"
  preset_apply browser_left - Применить пресет browser_left
  screenshot_preset_add myshot "My Screenshot" "~/screenshots/myshot.png" browser_left 10 10 800 600
  screenshot_preset_capture myshot - Сделать скриншот по пресету
  quick_capture browser_left myshot - Нормализовать окно browser_left и сделать скриншот myshot
  search chrome        - Найти все окна со словом "chrome" в заголовке
  screenshot 100 100 800 600 myshot "Мой скриншот" - Сделать скриншот
  screenshot_preview 100 100 800 600 - Скриншот с предварительным показом
""")


def parse_set_command(args: list[str]) -> tuple[int, dict]:
    """
    Парсит команду set.

    Args:
        args: Аргументы команды [id, x, y, w, h]

    Returns:
        Кортеж (window_id, параметры)
    """
    if len(args) < 2:
        raise ValueError("Недостаточно аргументов. Формат: set <id> [x] [y] [w] [h]")

    window_id = int(args[0])
    params = {}

    # Ожидаем до 4 дополнительных параметров
    param_names = ["x", "y", "width", "height"]
    for i, value in enumerate(args[1:5]):
        if value != "-":
            params[param_names[i]] = int(value)

    return window_id, params


def main() -> None:
    """Основная функция CLI."""
    print("=" * 80)
    print("Window Manager CLI - Управление окнами приложений")
    print("=" * 80)
    print_help()

    wm = WindowManager()
    normalizer = ProcessNormalizer(wm)
    storage = PresetStorage()
    screenshot_manager = ScreenshotManager()
    screenshot_preset_storage = ScreenshotPresetStorage()
    windows: list[WindowInfo] = []

    try:
        while True:
            try:
                command = input("\nwm> ").strip()
            except EOFError:
                print("\nВыход...")
                break

            if not command:
                continue

            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:]

            try:
                if cmd in ("list", "l"):
                    windows = wm.get_windows()
                    print_windows(windows)

                elif cmd in ("move",):
                    if len(args) != 3:
                        print("Ошибка: используйте 'move <id> <x> <y>'")
                        continue
                    window_id = int(args[0])
                    x, y = int(args[1]), int(args[2])
                    if wm.move_window(window_id, x, y):
                        print(f"Окно {window_id} перемещено в ({x}, {y})")
                    else:
                        print(f"Не удалось переместить окно {window_id}")

                elif cmd in ("resize",):
                    if len(args) != 3:
                        print("Ошибка: используйте 'resize <id> <width> <height>'")
                        continue
                    window_id = int(args[0])
                    width, height = int(args[1]), int(args[2])
                    if wm.resize_window(window_id, width, height):
                        print(f"Размер окна {window_id} изменен на {width}x{height}")
                    else:
                        print(f"Не удалось изменить размер окна {window_id}")

                elif cmd in ("focus",):
                    if len(args) != 1:
                        print("Ошибка: используйте 'focus <id>'")
                        continue
                    window_id = int(args[0])
                    if wm.focus_window(window_id):
                        print(f"Фокус установлен на окно {window_id}")
                    else:
                        print(f"Не удалось установить фокус на окно {window_id}")

                elif cmd in ("set",):
                    window_id, params = parse_set_command(args)
                    if wm.set_window_position_and_size(window_id, **params):
                        print(f"Параметры окна {window_id} обновлены: {params}")
                    else:
                        print(f"Не удалось обновить параметры окна {window_id}")

                elif cmd in ("normalize",):
                    if len(args) != 5:
                        print("Ошибка: используйте 'normalize <id> <x> <y> <width> <height>'")
                        continue
                    window_id = int(args[0])
                    x, y, width, height = int(args[1]), int(args[2]), int(args[3]), int(args[4])
                    if normalizer.normalize_window(window_id, x, y, width, height):
                        print(f"Окно {window_id} нормализовано: ({x}, {y}) {width}x{height}")
                    else:
                        print(f"Не удалось нормализовать окно {window_id}")

                elif cmd in ("search",):
                    query = " ".join(args)
                    results = normalizer.search_windows(query)
                    print_windows(results)

                elif cmd in ("presets", "p"):
                    presets = storage.get_all_presets()
                    print_presets(presets)

                elif cmd in ("preset_search",):
                    query = " ".join(args)
                    presets = storage.search_presets(query)
                    print_presets(presets)

                elif cmd in ("preset_apply",):
                    if len(args) != 1:
                        print("Ошибка: используйте 'preset_apply <preset_id>'")
                        continue
                    preset_id = args[0]
                    preset = storage.get_preset(preset_id)
                    if preset is None:
                        print(f"Пресет '{preset_id}' не найден")
                        continue
                    if normalizer.apply_preset(preset):
                        print(f"Пресет '{preset.name}' применен к окну '{preset.process_name}'")
                    else:
                        print(f"Не удалось применить пресет. Окно '{preset.process_name}' не найдено")

                elif cmd in ("preset_add",):
                    if len(args) < 7:
                        print("Ошибка: используйте 'preset_add <id> <name> <process> <x> <y> <width> <height> [description]'")
                        continue
                    preset_id = args[0]
                    name = args[1]
                    process_name = args[2]
                    x, y, width, height = int(args[3]), int(args[4]), int(args[5]), int(args[6])
                    description = args[7] if len(args) > 7 else ""
                    try:
                        storage.add_preset(preset_id, name, process_name, x, y, width, height, description)
                        print(f"Пресет '{name}' добавлен с ID '{preset_id}'")
                    except ValueError as e:
                        print(f"Ошибка: {e}")

                elif cmd in ("preset_remove",):
                    if len(args) != 1:
                        print("Ошибка: используйте 'preset_remove <preset_id>'")
                        continue
                    preset_id = args[0]
                    if storage.remove_preset(preset_id):
                        print(f"Пресет '{preset_id}' удален")
                    else:
                        print(f"Пресет '{preset_id}' не найден")

                elif cmd in ("preset_edit",):
                    if len(args) < 2:
                        print("Ошибка: используйте 'preset_edit <id> [--name=N] [--process=P] [--x=X] [--y=Y] [--w=W] [--h=H]'")
                        continue
                    preset_id = args[0]
                    kwargs = {}
                    for arg in args[1:]:
                        if arg.startswith("--name="):
                            kwargs["name"] = arg[7:]
                        elif arg.startswith("--process="):
                            kwargs["process_name"] = arg[10:]
                        elif arg.startswith("--x="):
                            kwargs["x"] = int(arg[4:])
                        elif arg.startswith("--y="):
                            kwargs["y"] = int(arg[4:])
                        elif arg.startswith("--w="):
                            kwargs["width"] = int(arg[4:])
                        elif arg.startswith("--h="):
                            kwargs["height"] = int(arg[4:])
                    
                    result = storage.update_preset(preset_id, **kwargs)
                    if result:
                        print(f"Пресет '{preset_id}' обновлен")
                    else:
                        print(f"Пресет '{preset_id}' не найден")

                elif cmd in ("refresh", "r"):
                    windows = wm.get_windows()
                    print(f"Список окон обновлен. Найдено {len(windows)} окон.")

                # Управление скриншотами
                elif cmd in ("screenshots", "ss"):
                    screenshots = screenshot_manager.get_all_screenshots()
                    print_screenshots(screenshots)

                elif cmd in ("screenshot",):
                    if len(args) < 4:
                        print("Ошибка: используйте 'screenshot <x> <y> <width> <height> [id] [description]'")
                        continue
                    x, y, width, height = int(args[0]), int(args[1]), int(args[2]), int(args[3])
                    screenshot_id = args[4] if len(args) > 4 else None
                    description = args[5] if len(args) > 5 else ""
                    try:
                        ss = screenshot_manager.capture(x, y, width, height, screenshot_id, description)
                        print(f"Скриншот сохранен с ID '{ss.id}': {ss.path}")
                    except ValueError as e:
                        print(f"Ошибка: {e}")
                    except RuntimeError as e:
                        print(f"Ошибка: {e}")

                elif cmd in ("screenshot_preview",):
                    if len(args) < 4:
                        print("Ошибка: используйте 'screenshot_preview <x> <y> <width> <height> [id] [description]'")
                        continue
                    x, y, width, height = int(args[0]), int(args[1]), int(args[2]), int(args[3])
                    screenshot_id = args[4] if len(args) > 4 else None
                    description = args[5] if len(args) > 5 else ""
                    try:
                        ss = screenshot_manager.capture_with_preview(x, y, width, height, screenshot_id, description)
                        print(f"Скриншот сохранен с ID '{ss.id}': {ss.path}")
                    except ValueError as e:
                        print(f"Ошибка: {e}")
                    except RuntimeError as e:
                        print(f"Ошибка: {e}")

                elif cmd in ("screenshot_remove",):
                    if len(args) != 1:
                        print("Ошибка: используйте 'screenshot_remove <id>'")
                        continue
                    screenshot_id = args[0]
                    if screenshot_manager.remove_screenshot(screenshot_id):
                        print(f"Скриншот '{screenshot_id}' удален")
                    else:
                        print(f"Скриншот '{screenshot_id}' не найден")

                elif cmd in ("screenshot_search",):
                    query = " ".join(args)
                    screenshots = screenshot_manager.search_screenshots(query)
                    print_screenshots(screenshots)

                # Управление пресетами скриншотов
                elif cmd in ("screenshot_presets", "sp"):
                    presets = screenshot_preset_storage.get_all_presets()
                    print_screenshot_presets(presets)

                elif cmd in ("screenshot_preset_search",):
                    query = " ".join(args)
                    presets = screenshot_preset_storage.search_presets(query)
                    print_screenshot_presets(presets)

                elif cmd in ("screenshot_preset_add",):
                    if len(args) < 8:
                        print("Ошибка: используйте 'screenshot_preset_add <id> <name> <path> <process_preset_id> <x> <y> <width> <height> [description]'")
                        continue
                    preset_id = args[0]
                    name = args[1]
                    screenshot_path = args[2]
                    process_preset_id = args[3]
                    x, y, width, height = int(args[4]), int(args[5]), int(args[6]), int(args[7])
                    description = args[8] if len(args) > 8 else ""
                    try:
                        screenshot_preset_storage.add_preset(
                            preset_id, name, screenshot_path, process_preset_id, x, y, width, height, description
                        )
                        print(f"Пресет скриншота '{name}' добавлен с ID '{preset_id}'")
                    except ValueError as e:
                        print(f"Ошибка: {e}")

                elif cmd in ("screenshot_preset_remove",):
                    if len(args) != 1:
                        print("Ошибка: используйте 'screenshot_preset_remove <id>'")
                        continue
                    preset_id = args[0]
                    if screenshot_preset_storage.remove_preset(preset_id):
                        print(f"Пресет скриншота '{preset_id}' удален")
                    else:
                        print(f"Пресет скриншота '{preset_id}' не найден")

                elif cmd in ("screenshot_preset_capture",):
                    if len(args) < 1:
                        print("Ошибка: используйте 'screenshot_preset_capture <preset_id> [screenshot_id]'")
                        continue
                    preset_id = args[0]
                    screenshot_id = args[1] if len(args) > 1 else None
                    preset = screenshot_preset_storage.get_preset(preset_id)
                    if preset is None:
                        print(f"Пресет скриншота '{preset_id}' не найден")
                        continue
                    try:
                        ss = screenshot_preset_storage.capture_with_preset(preset, screenshot_manager, screenshot_id)
                        print(f"Скриншот сохранен с ID '{ss.id}': {ss.path}")
                    except (ValueError, RuntimeError) as e:
                        print(f"Ошибка: {e}")

                elif cmd in ("quick_capture",):
                    if len(args) < 2:
                        print("Ошибка: используйте 'quick_capture <process_preset_id> <screenshot_preset_id> [screenshot_id]'")
                        continue
                    process_preset_id = args[0]
                    screenshot_preset_id = args[1]
                    screenshot_id = args[2] if len(args) > 2 else None
                    
                    # Получаем пресет нормализации
                    process_preset = storage.get_preset(process_preset_id)
                    if process_preset is None:
                        print(f"Пресет нормализации '{process_preset_id}' не найден")
                        continue
                    
                    # Получаем пресет скриншота
                    screenshot_preset = screenshot_preset_storage.get_preset(screenshot_preset_id)
                    if screenshot_preset is None:
                        print(f"Пресет скриншота '{screenshot_preset_id}' не найден")
                        continue
                    
                    # Проверяем что пресеты связаны
                    if screenshot_preset.process_preset_id != process_preset_id:
                        print(f"Предупреждение: пресет скриншота связан с процессом '{screenshot_preset.process_preset_id}', а не с '{process_preset_id}'")
                    
                    # Нормализуем окно
                    if normalizer.apply_preset(process_preset):
                        print(f"Окно нормализовано по пресету '{process_preset.name}'")
                        # Делаем скриншот
                        try:
                            ss = screenshot_preset_storage.capture_with_preset(screenshot_preset, screenshot_manager, screenshot_id)
                            print(f"Скриншот сохранен с ID '{ss.id}': {ss.path}")
                        except (ValueError, RuntimeError) as e:
                            print(f"Ошибка при создании скриншота: {e}")
                    else:
                        print(f"Не удалось нормализовать окно. Процесс '{process_preset.process_name}' не найден")

                elif cmd in ("help", "h"):
                    print_help()

                elif cmd in ("quit", "q"):
                    print("Выход...")
                    break

                else:
                    print(f"Неизвестная команда: {cmd}. Введите 'help' для справки.")

            except ValueError as e:
                print(f"Ошибка parsing: {e}")
            except Exception as e:
                print(f"Ошибка: {e}")

    except KeyboardInterrupt:
        print("\nПрервано пользователем.")


if __name__ == "__main__":
    main()
