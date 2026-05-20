"""
Консольный интерфейс для управления окнами.

Предоставляет простой CLI для тестирования функциональности WindowManager.
"""

import sys
from typing import Optional

from src.window_manager import WindowInfo, WindowManager


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


def print_help() -> None:
    """Выводит справку по командам."""
    print("""
Доступные команды:
  list, l              - Показать список всех окон
  move <id> <x> <y>    - Переместить окно с указанным ID в координаты (x, y)
  resize <id> <w> <h>  - Изменить размер окна на (width x height)
  focus <id>           - Сфокусироваться на окне
  set <id> [x] [y] [w] [h] - Установить позицию и/или размер 
                           (используйте '-' для пропуска параметра)
  refresh, r           - Обновить список окон
  help, h              - Показать эту справку
  quit, q              - Выйти из программы

Примеры:
  move 12345 100 200   - Переместить окно 12345 в точку (100, 200)
  resize 12345 800 600 - Изменить размер окна 12345 на 800x600
  set 12345 50 - 400 300 - Установить x=50, y без изменений, w=400, h=300
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

                elif cmd in ("refresh", "r"):
                    windows = wm.get_windows()
                    print(f"Список окон обновлен. Найдено {len(windows)} окон.")

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
