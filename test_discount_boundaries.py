"""Граничные тесты алгоритма скидки (домашнее задание пары 6).

Тесты работают с ВРЕМЕННОЙ копией базы, поэтому ваша база не меняется.
"""
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime

import discount
from models import Product
from test_discount import print_test_report


def add_order(db_path, date, product_id):
    """Добавляет тестовый заказ во временную базу."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO Заказ (дата, клиент, товар_id, количество) VALUES (?, 'Тест', ?, 1)",
        (date, product_id),
    )
    conn.commit()
    conn.close()


def run_tests():
    original_path = discount.DB_PATH
    tmp_dir = tempfile.mkdtemp()
    tmp_db = os.path.join(tmp_dir, "test.db")
    shutil.copy(original_path, tmp_db)
    discount.DB_PATH = tmp_db          # алгоритм работает с копией

    calc = discount.calculate_price_with_discount
    today = datetime(2026, 10, 15)

    # Добавляем заказы на границах периода (расчёт 15.10.2026, период 01.09–30.09)
    add_order(tmp_db, "2026-09-30", 4)   # последний день предыдущего месяца
    add_order(tmp_db, "2026-09-01", 5)   # первый день предыдущего месяца
    add_order(tmp_db, "2026-10-01", 6)   # текущий месяц — не считается
    add_order(tmp_db, "2026-08-31", 7)   # позапрошлый месяц — не считается

    negative_qty = Product(1, "Маргарита", "Пицца", 500, 600, -1, "", "")

    tests = [
        ("Заказ 30.09 (последний день месяца) → скидки нет", calc(4, 350, today), 350),
        ("Заказ 01.09 (первый день месяца) → скидки нет", calc(5, 550, today), 550),
        ("Заказ 01.10 (текущий месяц) → скидка есть", calc(6, 300, today), 225),
        ("Заказ 31.08 (позапрошлый месяц) → скидка есть", calc(7, 150, today), 112.5),
        ("Нулевая цена → результат 0", calc(4, 0, today), 0),
        ("Расчёт 31.10: период тот же (сентябрь), заказ 30.09 → скидки нет",
         calc(4, 350, datetime(2026, 10, 31)), 350),
        ("Отрицательное количество → товара «нет в наличии»", negative_qty.is_available(), False),
    ]

    discount.DB_PATH = original_path   # возвращаем настоящую базу
    shutil.rmtree(tmp_dir, ignore_errors=True)

    print("=" * 70)
    print("ГРАНИЧНЫЕ ТЕСТЫ АЛГОРИТМА СКИДКИ")
    print("=" * 70)
    passed = 0
    for comment, result, expected in tests:
        ok = result == expected
        passed += ok
        print(f"{'✅' if ok else '❌'} {comment}: получено {result} (ожидалось {expected})")
    print_test_report(passed, len(tests))


if __name__ == "__main__":
    run_tests()
