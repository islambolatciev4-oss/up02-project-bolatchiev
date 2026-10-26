"""Главный файл проекта УП.02 (вариант 22, «Доставка еды»).

Запуск:  python main.py
Выберите пункт меню — программа запустит нужную часть проекта.
"""
import subprocess
import sys

MENU = [
    ("Пара 2. task_01 — скидка по введённой цене", "task_01_discount.py"),
    ("Пара 2. task_02 — класс Product (обувь)", "task_02_class.py"),
    ("Пара 2. task_03 — каталог и итоговая сумма", "task_03_catalog.py"),
    ("Пара 2. task_04 — индикатор «много / мало»", "task_04_indicator.py"),
    ("Пара 3. Проверка подключения к БД", "db_test.py"),
    ("Пара 3. Структура базы данных", "show_structure.py"),
    ("Пара 3. Пять SQL-запросов", ["run_sql.py", "queries_pair3.sql"]),
    ("Пара 3. ДЗ — 10 SQL-запросов (queries.sql)", ["run_sql.py", "queries.sql"]),
    ("Пара 4. Проверка класса Product", "test_product.py"),
    ("Пара 4. Каталог товаров из БД (объекты Product)", "db_products.py"),
    ("Пара 4. Заказы из БД (объекты Order)", "db_orders.py"),
    ("Пара 5. Тесты алгоритма скидки (дополнительные)", "test_discount_extra.py"),
    ("Пара 6. Расширенные тесты алгоритма скидки", "test_discount.py"),
    ("Пара 6. ДЗ — граничные тесты", "test_discount_boundaries.py"),
]


def run(script):
    args = script if isinstance(script, list) else [script]
    print("\n" + "=" * 70)
    print("Запуск:", " ".join(args))
    print("=" * 70)
    subprocess.run([sys.executable, *args])


def main():
    while True:
        print("\n" + "=" * 70)
        print("ПРОЕКТ УП.02 — Болатчиев Ислам, вариант 22 (Доставка еды)")
        print("=" * 70)
        for i, (title, _) in enumerate(MENU, start=1):
            print(f"{i:>2}. {title}")
        print(" a. Запустить всё подряд (кроме пункта 1)")
        print(" 0. Выход")
        choice = input("Ваш выбор: ").strip().lower()
        if choice in ("0", "q", "exit", ""):
            break
        if choice == "a":
            for title, script in MENU[1:]:
                run(script)
        elif choice.isdigit() and 1 <= int(choice) <= len(MENU):
            run(MENU[int(choice) - 1][1])
        else:
            print("Нет такого пункта.")


if __name__ == "__main__":
    main()
