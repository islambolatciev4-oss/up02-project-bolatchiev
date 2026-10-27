"""Заказы: оформление (INSERT), остатки (UPDATE), список и состав (JOIN)."""
import sqlite3
from datetime import datetime

import config
from discount import calculate_price_with_discount

DATE_FORMAT = "%Y-%m-%d"


def get_connection():
    """Соединение для ручного управления транзакциями."""
    conn = sqlite3.connect(config.DB_PATH, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _today():
    return datetime.now().strftime(DATE_FORMAT)


def _validate_date(date_text):
    """Проверяет формат даты ГГГГ-ММ-ДД, возвращает строку."""
    try:
        return datetime.strptime(str(date_text).strip(), DATE_FORMAT).strftime(DATE_FORMAT)
    except ValueError:
        raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД (например, 2026-10-15)") from None


# ---------------------------------------------------------------- INSERT

def add_order_to_db(client, date=None):
    """Создаёт заказ (шапку) и возвращает его id."""
    date = _validate_date(date) if date else _today()
    conn = get_connection()
    try:
        cur = conn.execute("INSERT INTO Заказ (дата, клиент) VALUES (?, ?)", (date, client))
        return cur.lastrowid
    finally:
        conn.close()


def add_order_item(order_id, product_id, quantity, price):
    """Добавляет позицию в Состав_заказа."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Состав_заказа (заказ_id, товар_id, количество, цена) "
            "VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, price),
        )
    finally:
        conn.close()


def _merge_items(items):
    """Складывает одинаковые товары: [(id, кол-во), ...] → {id: кол-во}."""
    merged = {}
    for product_id, quantity in items:
        if int(quantity) <= 0:
            raise ValueError("Количество должно быть больше нуля")
        merged[int(product_id)] = merged.get(int(product_id), 0) + int(quantity)
    if not merged:
        raise ValueError("В заказе нет ни одной позиции")
    return merged


def create_order(client, items, date=None):
    """
    Оформляет заказ одной транзакцией: заказ + состав + списание остатков.

    :param client: ФИО клиента
    :param items: список пар (product_id, quantity)
    :param date: дата заказа (по умолчанию сегодня)
    :return: id нового заказа
    :raises ValueError: нет товара, не хватает остатка, неверное количество
    """
    merged = _merge_items(items)
    date = _validate_date(date) if date else _today()
    calc_date = datetime.strptime(date, DATE_FORMAT)

    # цены считаем до записи: у скидки своё (читающее) соединение
    prices = {}
    reader = get_connection()
    try:
        for product_id in merged:
            row = reader.execute("SELECT цена FROM Товар WHERE id = ?", (product_id,)).fetchone()
            if row is None:
                raise ValueError(f"Товар с id={product_id} не найден")
            prices[product_id] = round(
                calculate_price_with_discount(product_id, row[0], calc_date), 2
            )
    finally:
        reader.close()

    conn = get_connection()
    try:
        conn.execute("BEGIN")
        cur = conn.execute("INSERT INTO Заказ (дата, клиент) VALUES (?, ?)", (date, client))
        order_id = cur.lastrowid
        for product_id, quantity in merged.items():
            name, stock = conn.execute(
                "SELECT название, количество FROM Товар WHERE id = ?", (product_id,)
            ).fetchone()
            if quantity > stock:
                raise ValueError(f"Недостаточно товара «{name}»: в наличии {stock}, нужно {quantity}")
            conn.execute(
                "INSERT INTO Состав_заказа (заказ_id, товар_id, количество, цена) "
                "VALUES (?, ?, ?, ?)",
                (order_id, product_id, quantity, prices[product_id]),
            )
            updated = conn.execute(
                "UPDATE Товар SET количество = количество - ? WHERE id = ? AND количество >= ?",
                (quantity, product_id, quantity),
            )
            if updated.rowcount != 1:
                raise ValueError(f"Не удалось списать остаток товара «{name}»")
        conn.execute("COMMIT")
        return order_id
    except Exception:
        conn.execute("ROLLBACK")   # при любой ошибке заказ не сохраняется
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------- UPDATE

def get_product_quantity(product_id):
    """Остаток товара или None, если товара нет."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT количество FROM Товар WHERE id = ?", (product_id,)).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def update_product_quantity(product_id, new_quantity):
    """Устанавливает остаток товара (для администратора)."""
    new_quantity = int(new_quantity)
    if new_quantity < 0:
        raise ValueError("Остаток не может быть отрицательным")
    conn = get_connection()
    try:
        updated = conn.execute(
            "UPDATE Товар SET количество = ? WHERE id = ?", (new_quantity, product_id)
        )
        if updated.rowcount != 1:
            raise ValueError(f"Товар с id={product_id} не найден")
    finally:
        conn.close()


def decrease_product_quantity(product_id, quantity):
    """Уменьшает остаток (с проверкой, что хватает)."""
    conn = get_connection()
    try:
        updated = conn.execute(
            "UPDATE Товар SET количество = количество - ? WHERE id = ? AND количество >= ?",
            (quantity, product_id, quantity),
        )
        if updated.rowcount != 1:
            raise ValueError("Недостаточно товара на складе")
    finally:
        conn.close()


def restore_product_quantity(product_id, quantity):
    """Возвращает товар на склад."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE Товар SET количество = количество + ? WHERE id = ?", (quantity, product_id)
        )
    finally:
        conn.close()


def update_order_date(order_id, new_date):
    """Меняет дату заказа (администратор)."""
    new_date = _validate_date(new_date)
    conn = get_connection()
    try:
        updated = conn.execute("UPDATE Заказ SET дата = ? WHERE id = ?", (new_date, order_id))
        if updated.rowcount != 1:
            raise ValueError(f"Заказ №{order_id} не найден")
    finally:
        conn.close()


def delete_order_item(item_id):
    """Удаляет позицию заказа и возвращает товар на склад (одной транзакцией)."""
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        row = conn.execute(
            "SELECT товар_id, количество FROM Состав_заказа WHERE id = ?", (item_id,)
        ).fetchone()
        if row is None:
            raise ValueError("Позиция заказа не найдена")
        product_id, quantity = row
        conn.execute("DELETE FROM Состав_заказа WHERE id = ?", (item_id,))
        conn.execute(
            "UPDATE Товар SET количество = количество + ? WHERE id = ?", (quantity, product_id)
        )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------- SELECT / JOIN

def get_last_order_id():
    """id последнего заказа или None."""
    conn = get_connection()
    try:
        return conn.execute("SELECT MAX(id) FROM Заказ").fetchone()[0]
    finally:
        conn.close()


def get_all_orders():
    """Список заказов (новые сверху): (id, дата, клиент)."""
    conn = get_connection()
    try:
        return conn.execute("SELECT id, дата, клиент FROM Заказ ORDER BY id DESC").fetchall()
    finally:
        conn.close()


def get_orders_by_client(client):
    """Заказы клиента: (id, дата, клиент)."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT id, дата, клиент FROM Заказ WHERE клиент = ? ORDER BY id DESC", (client,)
        ).fetchall()
    finally:
        conn.close()


def get_order_by_id(order_id):
    """Один заказ: (id, дата, клиент) или None."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT id, дата, клиент FROM Заказ WHERE id = ?", (order_id,)
        ).fetchone()
    finally:
        conn.close()


def get_order_items(order_id):
    """Состав заказа через JOIN: (id позиции, название, количество, цена, сумма)."""
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT Состав_заказа.id, Товар.название, Состав_заказа.количество,
                   Состав_заказа.цена,
                   Состав_заказа.количество * Состав_заказа.цена AS сумма
            FROM Состав_заказа
            JOIN Товар ON Состав_заказа.товар_id = Товар.id
            WHERE Состав_заказа.заказ_id = ?
            ORDER BY Состав_заказа.id
            """,
            (order_id,),
        ).fetchall()
    finally:
        conn.close()


def get_order_total(order_id):
    """Сумма заказа."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT SUM(количество * цена) FROM Состав_заказа WHERE заказ_id = ?", (order_id,)
        ).fetchone()
        return round(row[0] or 0, 2)
    finally:
        conn.close()
