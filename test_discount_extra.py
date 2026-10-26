"""Дополнительные тесты алгоритма скидки (домашнее задание)."""
from datetime import datetime
from discount import calculate_price_with_discount, get_previous_month_range


def run_tests():
    test_cases = [
        # (дата расчёта, id, цена, ожидание, пояснение)
        (datetime(2026, 11, 15), 1, 600, 450, "Ноябрь: в октябре заказов нет → скидка"),
        (datetime(2026, 10, 1), 2, 800, 800, "1 октября: сентябрь, есть заказ → без скидки"),
        (datetime(2026, 10, 31), 3, 400, 400, "31 октября: сентябрь, есть заказ → без скидки"),
        (datetime(2026, 9, 15), 1, 600, 450, "Сентябрь: в августе заказов нет → скидка"),
        (datetime(2027, 1, 10), 7, 150, 112.5, "Январь: прошлый месяц — декабрь 2026 → скидка"),
    ]

    print("=" * 60)
    print("ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ")
    print("=" * 60)

    passed = 0
    for date, product_id, price, expected, comment in test_cases:
        result = calculate_price_with_discount(product_id, price, date)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"{status} {date:%d.%m.%Y}, товар {product_id}: {price} → {result} "
              f"(ожидалось {expected}) — {comment}")

    print("-" * 60)
    # Проверка границ периода (переход через год)
    start, end = get_previous_month_range(datetime(2027, 1, 10))
    ok = (start, end) == ("2026-12-01", "2026-12-31")
    print(f"{'✅' if ok else '❌'} Диапазон для 10.01.2027: {start} — {end}")
    passed += ok

    print("=" * 60)
    print(f"Пройдено: {passed} / {len(test_cases) + 1}")


if __name__ == "__main__":
    run_tests()
