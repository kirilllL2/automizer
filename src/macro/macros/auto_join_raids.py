"""
Макрос для автоматического присоединения к рейдам.

Последовательность действий:
1. Фокус на окне процесса
2. Найти область по пресету bottom_nav_aliance в нижнем навигационном меню
3. Кликнуть в этой области (с использованием default_click_percent из конфига)
4. Найти кнопку по пресету aliance_news и кликнуть в области
5. Проверить, что вкладка "рейды" активна (по пресету aliance_news_raids-selected)
6. Если не активна - кликнуть на неактивную кнопку рейда (aliance_news_raids-unselected)
7. Вывести сообщение "Рейды открыты"
8. Запустить цикл поиска рейдов (каждые 15 секунд):
   - Искать кнопку присоединения (aliance_news_raids-can_join_raid)
   - Если найдена - кликнуть, затем найти кнопку отправки (join_raid-send) и кликнуть
   - Затем нажать на кнопку "Выбранных рейдов" (aliance_news_raids-selected)
   - Если какую-то кнопку не удалось найти - кликнуть на вкладку рейдов
"""

# Метаданные макроса
NAME = "Авто-присоединение к рейдам"
DESCRIPTION = "Автоматически открывает вкладку рейдов и присоединяется к доступным рейдам"

# Импортируем действия из модуля macro
from src.macro import (
    click_in_region,
    find_region,
    focus_window,
    delay,
    find_window_by_process,
    click_in_window_region,
)
import random
import time
import signal
import sys

# Флаг для контроля остановки скрипта
stop_requested = False

def signal_handler(signum, frame):
    """Обработчик сигнала прерывания (Ctrl+C)"""
    global stop_requested
    print("\n[Инфо] Получен сигнал остановки. Завершаем работу...")
    stop_requested = True

# Регистрируем обработчик сигнала
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def click_on_raids_tab(window_id: int):
    """
    Кликает на вкладку рейдов (кнопку aliance_news_raids-unselected или aliance_news_raids-selected).
    
    Args:
        window_id: Handle окна.
    """
    print("[Инфо] Клик по вкладке рейдов...")
    
    # Сначала пробуем найти неактивную кнопку рейдов
    raids_region = find_region("aliance_news_raids-unselected")
    
    if not raids_region:
        # Если не найдена, пробуем найти активную кнопку
        raids_region = find_region("aliance_news_raids-selected")
    
    if raids_region:
        click_in_window_region(window_id, raids_region)
        delay(0.5)
        print("[Инфо] Успешный клик по вкладке рейдов")
    else:
        print("[Предупреждение] Не удалось найти кнопку вкладки рейдов")


def try_join_raid(window_id: int) -> bool:
    """
    Пытается присоединиться к рейду.
    
    Args:
        window_id: Handle окна.
    
    Returns:
        True, если успешно присоединился, False иначе.
    """
    print("[Цикл] Поиск доступного рейда для присоединения...")
    
    # Шаг 1: Ищем кнопку присоединения к рейду
    can_join_region = find_region("aliance_news_raids-can_join_raid")
    
    if not can_join_region:
        print("[Цикл] Кнопка присоединения не найдена, клик по вкладке рейдов")
        click_on_raids_tab(window_id)
        return False
    
    print(f"[Цикл] Найдена кнопка присоединения: {can_join_region}")
    
    # Кликаем на кнопку присоединения
    click_in_window_region(window_id, can_join_region)
    delay(1.0)
    
    # Шаг 2: Ищем кнопку отправки
    print("[Цикл] Поиск кнопки отправки...")
    send_region = find_region("join_raid-send")
    
    if not send_region:
        print("[Цикл] Кнопка отправки не найдена, клик по вкладке рейдов")
        click_on_raids_tab(window_id)
        return False
    
    print(f"[Цикл] Найдена кнопка отправки: {send_region}")
    
    # Кликаем на кнопку отправки
    click_in_window_region(window_id, send_region)
    delay(1.0)
    
    # Шаг 3: Ищем кнопку "Выбранных рейдов" (aliance_news_raids-selected)
    print("[Цикл] Поиск кнопки 'Выбранных рейдов'...")
    all_sended_region = find_region("aliance_news_raids-selected")
    
    if not all_sended_region:
        print("[Цикл] Кнопка 'Выбранных рейдов' не найдена, клик по вкладке рейдов")
        click_on_raids_tab(window_id)
        return False
    
    print(f"[Цикл] Найдена кнопка 'Выбранных рейдов': {all_sended_region}")
    
    # Кликаем на кнопку "Выбранных рейдов"
    click_in_window_region(window_id, all_sended_region)
    delay(0.5)
    
    print("[Цикл] Успешно присоединился к рейду!")
    return True


def run():
    """
    Основная функция макроса.
    Выполняет последовательность действий для открытия вкладки рейдов
    и циклического поиска доступных рейдов.
    """
    print("Начало выполнения макроса 'Авто-присоединение к рейдам'")
    
    # Шаг 1: Фокус на окне процесса и получаем его handle
    print("[Шаг 1] Фокусировка на окне процесса...")
    if not focus_window("tilesauto"):
        print("[Ошибка] Не удалось сфокусироваться на окне. Прерывание макроса.")
        return
    
    # Получаем handle окна для низкоуровневых операций
    window_id = find_window_by_process("tilesauto")
    if not window_id:
        print("[Ошибка] Не удалось получить handle окна. Прерывание макроса.")
        return
    
    # Небольшая задержка после фокуса
    delay(0.5)
    
    # Шаг 2: Найти область кнопки альянса в нижнем меню
    print("[Шаг 2] Поиск кнопки альянса (bottom_nav_aliance)...")
    aliance_btn_region = find_region("bottom_nav_aliance")
    
    if not aliance_btn_region:
        print("[Ошибка] Кнопка альянса не найдена. Прерывание макроса.")
        return
    
    print(f"[Успех] Кнопка альянса найдена: {aliance_btn_region}")
    
    # Шаг 3: Кликнуть в области кнопки альянса через низкоуровневый клик
    print("[Шаг 3] Клик по кнопке альянса (низкоуровневый)...")
    click_in_window_region(window_id, aliance_btn_region)
    
    # Задержка для открытия окна альянса
    delay(1.0)
    
    # Шаг 4: Найти кнопку news в окне альянса
    print("[Шаг 4] Поиск кнопки новостей (aliance_news)...")
    aliance_news_region = find_region("aliance_news")
    
    if not aliance_news_region:
        print("[Ошибка] Кнопка новостей альянса не найдена. Прерывание макроса.")
        return
    
    print(f"[Успех] Кнопка новостей найдена: {aliance_news_region}")
    
    # Кликнуть в области кнопки новостей через низкоуровневый клик
    print("[Шаг 5] Клик по кнопке новостей (низкоуровневый)...")
    click_in_window_region(window_id, aliance_news_region)
    
    # Задержка для загрузки вкладки
    delay(1.0)
    
    # Шаг 6: Проверить, активна ли вкладка "рейды"
    print("[Шаг 6] Проверка активности вкладки 'рейды'...")
    
    # Проверяем, есть ли активная вкладка рейдов
    raids_selected_region = find_region("aliance_news_raids-selected")
    
    if raids_selected_region:
        print("[Инфо] Вкладка 'рейды' уже активна")
    else:
        print("[Инфо] Вкладка 'рейды' не активна, переключаем...")
        
        # Ищем неактивную кнопку рейдов
        raids_unselected_region = find_region("aliance_news_raids-unselected")
        
        if not raids_unselected_region:
            print("[Ошибка] Кнопка переключения на рейды не найдена.")
            return
        
        # Кликаем на неактивную кнопку рейдов через низкоуровневый клик
        print("[Шаг 7] Клик по кнопке 'рейды' (низкоуровневый)...")
        click_in_window_region(window_id, raids_unselected_region)
        
        # Задержка для переключения
        delay(0.5)
    
    # Финальное сообщение об успешном открытии рейдов
    print("=" * 50)
    print("Рейды открыты")
    print("=" * 50)
    
    # Запуск цикла поиска рейдов
    print("=" * 50)
    print("Запуск цикла поиска рейдов (каждые 15 секунд)")
    print("=" * 50)
    
    iteration = 0
    while not stop_requested:
        iteration += 1
        print(f"\n[Цикл] === Итерация {iteration} ===")
        
        # Пытаемся присоединиться к рейду
        success = try_join_raid(window_id)
        
        if success:
            print("[Цикл] Рейд найден и присоединение выполнено!")
        else:
            print("[Цикл] Присоединение не выполнено, продолжаем поиск...")
        
        # Ждем 15 секунд перед следующей проверкой
        print(f"[Цикл] Ожидание 15 секунд до следующей проверки...")
        for i in range(15, 0, -1):
            if stop_requested:
                break
            print(f"[Цикл] Осталось секунд: {i}", end="\r")
            time.sleep(1)
        
        if not stop_requested:
            print()  # Новая строка после обратного отсчета
    
    print("\n[Инфо] Макрос завершен.")
    
    # Удаляем обработчики сигналов при выходе
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
