"""Загрузка товаров из БД: каталог, категории, низкий остаток."""
import sqlite3
from config import DB_PATH


def _select(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def get_all_products():
    return _select("SELECT * FROM Товар ORDER BY id")


def get_products_by_category(category):
    return _select("SELECT * FROM Товар WHERE категория = ?", (category,))


def get_products_low_stock():
    return _select("SELECT * FROM Товар WHERE количество <= 3")


def get_categories():
    rows = _select("SELECT DISTINCT категория FROM Товар ORDER BY категория")
    return [row[0] for row in rows]


def print_catalog(products):
    print(f"\n{'=' * 60}")
    print(f"КАТАЛОГ ({len(products)} товаров)")
    print("=" * 60)
    for p in products:
        name = p["название"]
        category = p["категория"]
        price = p["цена"]
        qty = p["количество"]
        indicator = "много" if qty > 5 else "мало"
        highlight = "⚠️" if qty <= 3 else "  "
        print(f"{highlight} {name} ({category})")
        print(f"   Цена: {price} руб. | Кол-во: {qty} ({indicator})")
    print("=" * 60)


if __name__ == "__main__":
    print("1. Все товары")
    print_catalog(get_all_products())

    print("\n2. Категории:")
    for cat in get_categories():
        print(f"   - {cat}")

    print("\n3. Товары с низким остатком (≤3):")
    print_catalog(get_products_low_stock())