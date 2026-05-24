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
"""

# Метаданные макроса
NAME = "Авто-присоединение к рейдам"
DESCRIPTION = "Автоматически открывает вкладку рейдов в альянсе"

# Импортируем действия из модуля macro
from src.macro import (
    click_in_region,
    find_region,
    focus_window,
    delay,
)


def run():
    """
    Основная функция макроса.
    Выполняет последовательность действий для открытия вкладки рейдов.
    """
    print("Начало выполнения макроса 'Авто-присоединение к рейдам'")
    
    # Шаг 1: Фокус на окне процесса
    print("[Шаг 1] Фокусировка на окне процесса...")
    if not focus_window("tilesauto"):
        print("[Ошибка] Не удалось сфокусироваться на окне. Прерывание макроса.")
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
    
    # Шаг 3: Кликнуть в области кнопки альянса (используется default_click_percent из конфига)
    print("[Шаг 3] Клик по кнопке альянса...")
    click_in_region(aliance_btn_region)
    
    # Задержка для открытия окна альянса
    delay(1.0)
    
    # Шаг 4: Найти кнопку news в окне альянса
    print("[Шаг 4] Поиск кнопки новостей (aliance_news)...")
    aliance_news_region = find_region("aliance_news")
    
    if not aliance_news_region:
        print("[Ошибка] Кнопка новостей альянса не найдена. Прерывание макроса.")
        return
    
    print(f"[Успех] Кнопка новостей найдена: {aliance_news_region}")
    
    # Кликнуть в области кнопки новостей
    print("[Шаг 5] Клик по кнопке новостей...")
    click_in_region(aliance_news_region)
    
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
        
        # Кликаем на неактивную кнопку рейдов
        print("[Шаг 7] Клик по кнопке 'рейды'...")
        click_in_region(raids_unselected_region)
        
        # Задержка для переключения
        delay(0.5)
    
    # Финальное сообщение
    print("=" * 50)
    print("Рейды открыты")
    print("=" * 50)
    print("Макрос завершен успешно")
