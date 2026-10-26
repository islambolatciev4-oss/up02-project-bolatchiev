"""Загрузка товаров из БД в объекты класса Product."""
import sqlite3
from config import DB_PATH
from models import Product


def _row_to_product(row):
    """Превращает строку таблицы Товар в объект Product."""
    return Product(
        product_id=row["id"],
        name=row["название"],
        category=row["категория"],
        weight=row["вес"],
        price=row["цена"],
        quantity=row["количество"],
        image=row["фото"],
        composition=row["состав"],
    )


def _select_products(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    return [_row_to_product(row) for row in rows]


def get_all_products():
    """Возвращает список объектов Product из БД."""
    return _select_products("SELECT * FROM Товар ORDER BY id")


def get_product_by_id(product_id):
    """Возвращает один товар по id или None."""
    products = _select_products("SELECT * FROM Товар WHERE id = ?", (product_id,))
    return products[0] if products else None


def get_products_by_category(category):
    """Возвращает список объектов Product по категории."""
    return _select_products("SELECT * FROM Товар WHERE категория = ?", (category,))


def get_products_low_stock():
    """Возвращает товары с количеством ≤ 3."""
    return _select_products("SELECT * FROM Товар WHERE количество <= 3")


def print_products(products):
    """Выводит информацию о товарах."""
    print(f"\nВсего товаров: {len(products)}\n")
    for p in products:
        print(p.info())
        print("-" * 60)


def print_catalog_with_highlight(products):
    """Выводит каталог с подсветкой для товаров ≤3."""
    print(f"\n{'=' * 70}")
    print(f"КАТАЛОГ ({len(products)} товаров)")
    print("=" * 70)
    for p in products:
        highlight = "⚠️" if p.quantity <= 3 else "  "
        print(f"{highlight} {p.info()}")
    print("=" * 70)


if __name__ == "__main__":
    print("1. Все товары:")
    print_catalog_with_highlight(get_all_products())

    print("\n2. Товары категории «Пицца»:")
    print_catalog_with_highlight(get_products_by_category("Пицца"))

    print("\n3. Товары с низким остатком (≤3):")
    print_catalog_with_highlight(get_products_low_stock())
