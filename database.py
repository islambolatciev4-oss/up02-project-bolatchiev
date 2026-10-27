"""Работа с базой данных: товары и пользователи."""
import sqlite3

import config

# Индексы полей товара в кортеже (порядок задаёт SELECT ниже)
P_ID, P_CATEGORY, P_NAME, P_WEIGHT, P_PRICE, P_QTY, P_IMAGE, P_COMPOSITION = range(8)

PRODUCT_SELECT = (
    "SELECT id, категория, название, вес, цена, количество, фото, состав "
    "FROM Товар"
)

# Индексы пользователя: (id, фамилия, имя, отчество, логин, роль)
U_ID, U_LAST, U_FIRST, U_MIDDLE, U_LOGIN, U_ROLE = range(6)


def get_connection():
    """Открывает соединение с БД."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _fetch_all(sql, params=()):
    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def get_all_products():
    """Возвращает список товаров (кортежи в порядке P_*)."""
    return _fetch_all(PRODUCT_SELECT + " ORDER BY id")


def get_product_by_id(product_id):
    """Возвращает товар по id или None."""
    rows = _fetch_all(PRODUCT_SELECT + " WHERE id = ?", (product_id,))
    return rows[0] if rows else None


def get_user_by_login(login):
    """
    Ищет пользователя по логину (пароль не требуется — условие КИМ).

    :param login: логин
    :return: кортеж (id, фамилия, имя, отчество, логин, роль) или None
    """
    rows = _fetch_all(
        """
        SELECT Пользователь.id, Пользователь.фамилия, Пользователь.имя,
               Пользователь.отчество, Пользователь.логин, Роль.название
        FROM Пользователь
        JOIN Роль ON Пользователь.роль_id = Роль.id
        WHERE Пользователь.логин = ?
        """,
        (login,),
    )
    return rows[0] if rows else None


def get_all_users():
    """Возвращает всех пользователей (для проверки и тестов)."""
    return _fetch_all(
        """
        SELECT Пользователь.id, Пользователь.фамилия, Пользователь.имя,
               Пользователь.отчество, Пользователь.логин, Роль.название
        FROM Пользователь
        JOIN Роль ON Пользователь.роль_id = Роль.id
        ORDER BY Пользователь.id
        """
    )
