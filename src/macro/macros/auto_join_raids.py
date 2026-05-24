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
   - Затем нажать на кнопку "Выбранных рейдов" (join_raid-all_sended)
   - Если какую-то кнопку не удалось найти - кликнуть в случайном месте в области рейдов
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
    Region,
)
import random
import time


def get_raids_search_region(window_id: int) -> Region:
    """
    Возвращает область для поиска рейдов на основе положения элементов интерфейса.
    Использует координаты известных элементов для определения области вкладки рейдов.
    """
    # Примерные координаты области контента рейдов (на основе пресетов)
    # aliance_news_raids-empty_raids имеет x: 250, y: 300
    # join_raid-send имеет x: 480, y: 767
    # Создаем область, охватывающую основную часть вкладки рейдов
    return Region(x1=200, y1=150, x2=800, y2=850)


def click_random_in_raids_region(window_id: int, raids_region: Region):
    """
    Кликает в случайное место в области вкладки с рейдами.
    
    Args:
        window_id: Handle окна.
        raids_region: Область для случайного клика.
    """
    print("[Инфо] Клик в случайном месте области рейдов...")
    click_in_window_region(window_id, raids_region, percent=0.5, distribution="uniform")
    delay(0.5)


def try_join_raid(window_id: int, raids_region: Region) -> bool:
    """
    Пытается присоединиться к рейду.
    
    Args:
        window_id: Handle окна.
        raids_region: Область вкладки рейдов для fallback кликов.
    
    Returns:
        True, если успешно присоединился, False иначе.
    """
    print("[Цикл] Поиск доступного рейда для присоединения...")
    
    # Шаг 1: Ищем кнопку присоединения к рейду
    can_join_region = find_region("aliance_news_raids-can_join_raid")
    
    if not can_join_region:
        print("[Цикл] Кнопка присоединения не найдена, клик в случайном месте")
        click_random_in_raids_region(window_id, raids_region)
        return False
    
    print(f"[Цикл] Найдена кнопка присоединения: {can_join_region}")
    
    # Кликаем на кнопку присоединения
    click_in_window_region(window_id, can_join_region)
    delay(1.0)
    
    # Шаг 2: Ищем кнопку отправки
    print("[Цикл] Поиск кнопки отправки...")
    send_region = find_region("join_raid-send")
    
    if not send_region:
        print("[Цикл] Кнопка отправки не найдена, клик в случайном месте")
        click_random_in_raids_region(window_id, raids_region)
        return False
    
    print(f"[Цикл] Найдена кнопка отправки: {send_region}")
    
    # Кликаем на кнопку отправки
    click_in_window_region(window_id, send_region)
    delay(1.0)
    
    # Шаг 3: Ищем кнопку "Выбранных рейдов" (join_raid-all_sended)
    print("[Цикл] Поиск кнопки 'Выбранных рейдов'...")
    all_sended_region = find_region("join_raid-all_sended")
    
    if not all_sended_region:
        print("[Цикл] Кнопка 'Выбранных рейдов' не найдена, клик в случайном месте")
        click_random_in_raids_region(window_id, raids_region)
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
    
    # Определяем область рейдов для fallback кликов
    raids_search_region = get_raids_search_region(window_id)
    print(f"[Инфо] Область поиска рейдов: {raids_search_region}")
    
    # Запуск цикла поиска рейдов
    print("=" * 50)
    print("Запуск цикла поиска рейдов (каждые 15 секунд)")
    print("=" * 50)
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n[Цикл] === Итерация {iteration} ===")
        
        # Пытаемся присоединиться к рейду
        success = try_join_raid(window_id, raids_search_region)
        
        if success:
            print("[Цикл] Рейд найден и присоединение выполнено!")
        else:
            print("[Цикл] Присоединение не выполнено, продолжаем поиск...")
        
        # Ждем 15 секунд перед следующей проверкой
        print(f"[Цикл] Ожидание 15 секунд до следующей проверки...")
        for i in range(15, 0, -1):
            print(f"[Цикл] Осталось секунд: {i}", end="\r")
            time.sleep(1)
        print()  # Новая строка после обратного отсчета
