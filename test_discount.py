"""Тестирование алгоритма скидки (расширенные тесты, пара 6)."""
from datetime import datetime

from discount import calculate_price_with_discount


def print_test_report(passed, total):
    """Выводит итоговый отчёт о тестировании."""
    result = "✅ УСПЕХ" if passed == total else "❌ ЕСТЬ ОШИБКИ"
    print("=" * 40)
    print("ОТЧЁТ О ТЕСТИРОВАНИИ")
    print(f"Пройдено: {passed} / {total}")
    print(f"Результат: {result}")
    print("=" * 40)


def run_tests():
    test_cases = [
        # (product_id, price, date, expected, comment)
        (1, 600, datetime(2026, 10, 15), 600, "Маргарита — заказ есть в сентябре"),
        (4, 350, datetime(2026, 10, 15), 262.5, "Цезарь — заказов нет → скидка"),
        (3, 400, datetime(2026, 10, 15), 400, "Чизбургер — заказ есть в сентябре"),
        (6, 300, datetime(2026, 10, 15), 225, "Тирамису — заказов нет → скидка"),
        (7, 150, datetime(2026, 10, 15), 112.5, "Лимонад — заказов нет → скидка"),

        # Новые тесты (из тетради, под данные варианта 22)
        (2, 800, datetime(2026, 11, 15), 600, "Ноябрь: в октябре заказов не было → скидка"),
        (1, 600, datetime(2026, 11, 15), 450, "Ноябрь: заказ был в сентябре, а не в октябре → скидка"),
        (4, 350, datetime(2026, 9, 1), 262.5, "Август — заказов нет → скидка"),

        # Мои тесты
        (5, 550, datetime(2026, 10, 15), 412.5, "Карбонара — заказов нет → скидка"),
        (2, 800, datetime(2026, 10, 1), 800, "1 октября: сентябрь, заказ есть → без скидки"),
        (3, 400, datetime(2027, 1, 1), 300, "1 января: прошлый месяц — декабрь, заказов нет → скидка"),
    ]

    print("=" * 70)
    print("РАСШИРЕННОЕ ТЕСТИРОВАНИЕ АЛГОРИТМА СКИДКИ")
    print("=" * 70)

    passed = 0
    for product_id, price, date, expected, comment in test_cases:
        result = calculate_price_with_discount(product_id, price, date)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} Товар {product_id} на {date.date()}: "
              f"{price} → {result} (ожидалось {expected}) — {comment}")

    print("=" * 70)
    print(f"Пройдено: {passed} / {len(test_cases)}")
    print_test_report(passed, len(test_cases))


if __name__ == "__main__":
    run_tests()
