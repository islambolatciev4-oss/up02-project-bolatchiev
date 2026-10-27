import database as db

def test_db_available():
    try:
        products = db.get_all_products()
        return isinstance(products, list)
    except Exception as e:
        print(f"❌ БД недоступна: {e}")
        return False

def test_products_count():
    products = db.get_all_products()
    return len(products) > 0

def test_product_fields():
    products = db.get_all_products()
    for p in products:
        if len(p) < 8:
            print(f"❌ Товар id={p[0]}: мало полей ({len(p)})")
            return False
    return True

def test_prices_are_numbers():
    products = db.get_all_products()
    for p in products:
        if not isinstance(p[5], (int, float)):
            print(f"❌ Товар id={p[0]}: цена не число")
            return False
    return True

def test_quantity_not_negative():
    products = db.get_all_products()
    for p in products:
        if p[6] < 0:
            print(f"❌ Товар id={p[0]}: отрицательное количество")
            return False
    return True

def test_names_not_empty():
    products = db.get_all_products()
    for p in products:
        if not p[1]:
            print(f"❌ Товар id={p[0]}: пустое название")
            return False
    return True

def run_all_tests():
    tests = [
        ("БД доступна", test_db_available),
        ("Товары загружены", test_products_count),
        ("У всех товаров нужные поля", test_product_fields),
        ("Все цены — числа", test_prices_are_numbers),
        ("Количество не отрицательное", test_quantity_not_negative),
        ("Названия не пустые", test_names_not_empty),
    ]
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ КАТАЛОГА")
    print("=" * 60)
    passed = 0
    for name, func in tests:
        result = func()
        status = "✅" if result else "❌"
        if result:
            passed += 1
        print(f"{status} {name}")
    print("=" * 60)
    print(f"Пройдено: {passed} / {len(tests)}")

if __name__ == "__main__":
    run_all_tests()
