"""Загрузка заказов из БД в объекты класса Order."""
import sqlite3
from config import DB_PATH
from models import Order
from db_products import get_product_by_id


def get_all_orders():
    """Возвращает список объектов Order из БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT * FROM Заказ ORDER BY id").fetchall()
    finally:
        conn.close()

    orders = []
    for row in rows:
        product = get_product_by_id(row["товар_id"])
        orders.append(
            Order(
                order_id=row["id"],
                date=row["дата"],
                client=row["клиент"],
                product=product,
                quantity=row["количество"],
            )
        )
    return orders


def print_orders(orders):
    """Выводит заказы в консоль."""
    print(f"\nВсего заказов: {len(orders)}\n")
    for o in orders:
        print(o.info())
        print(f"   Стоимость: {o.total()} руб.")
        print("-" * 60)


if __name__ == "__main__":
    print_orders(get_all_orders())
