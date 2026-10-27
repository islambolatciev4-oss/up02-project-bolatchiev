"""Подготовка схемы БД для пар 22–27: состав заказа, роли, пользователи.

Запускается автоматически при старте приложения (ensure_schema) и безопасна
при повторных запусках. Старые данные сохраняются.
"""
import sqlite3

import config

ROLES = ("Клиент", "Менеджер", "Администратор")


def _columns(conn, table):
    return {row[1]: row for row in conn.execute(f'PRAGMA table_info("{table}")')}


def _table_exists(conn, table):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()
    return row is not None


def _make_order_header_flexible(conn):
    """Заказ: товар_id и количество больше не обязательны (позиции — в Состав_заказа)."""
    cols = _columns(conn, "Заказ")
    if "товар_id" not in cols or cols["товар_id"][3] == 0:
        return   # уже гибкая схема
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("BEGIN")
    conn.execute(
        """
        CREATE TABLE Заказ_новый (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            дата TEXT NOT NULL,
            клиент TEXT NOT NULL,
            товар_id INTEGER,
            количество INTEGER,
            FOREIGN KEY (товар_id) REFERENCES Товар(id)
        )
        """
    )
    conn.execute(
        "INSERT INTO Заказ_новый (id, дата, клиент, товар_id, количество) "
        "SELECT id, дата, клиент, товар_id, количество FROM Заказ"
    )
    conn.execute("DROP TABLE Заказ")
    conn.execute("ALTER TABLE Заказ_новый RENAME TO Заказ")
    conn.execute("COMMIT")
    conn.execute("PRAGMA foreign_keys = ON")


def _create_order_items(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS Состав_заказа (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            заказ_id INTEGER NOT NULL,
            товар_id INTEGER NOT NULL,
            количество INTEGER NOT NULL CHECK (количество > 0),
            цена REAL NOT NULL,
            FOREIGN KEY (заказ_id) REFERENCES Заказ(id) ON DELETE CASCADE,
            FOREIGN KEY (товар_id) REFERENCES Товар(id)
        )
        """
    )
    # Переносим позиции старых заказов (по одному товару в заказе)
    conn.execute(
        """
        INSERT INTO Состав_заказа (заказ_id, товар_id, количество, цена)
        SELECT Заказ.id, Заказ.товар_id, Заказ.количество, Товар.цена
        FROM Заказ
        JOIN Товар ON Товар.id = Заказ.товар_id
        WHERE Заказ.товар_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM Состав_заказа WHERE Состав_заказа.заказ_id = Заказ.id
          )
        """
    )


def _create_roles_and_users(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS Роль ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, название TEXT NOT NULL UNIQUE)"
    )
    for role in ROLES:
        conn.execute("INSERT OR IGNORE INTO Роль (название) VALUES (?)", (role,))

    cols = _columns(conn, "Пользователь")
    for name in ("фамилия", "имя", "отчество"):
        if name not in cols:
            conn.execute(f'ALTER TABLE Пользователь ADD COLUMN "{name}" TEXT')
    if "роль_id" not in cols:
        conn.execute('ALTER TABLE Пользователь ADD COLUMN "роль_id" INTEGER REFERENCES Роль(id)')

    rows = conn.execute(
        "SELECT id, фио, роль, фамилия, роль_id FROM Пользователь"
    ).fetchall()
    for user_id, fio, role, last, role_id in rows:
        if last and role_id:
            continue
        parts = (fio or "").split()
        parts += [""] * (3 - len(parts))
        role_row = conn.execute("SELECT id FROM Роль WHERE название = ?", (role,)).fetchone()
        conn.execute(
            "UPDATE Пользователь SET фамилия = ?, имя = ?, отчество = ?, роль_id = ? WHERE id = ?",
            (parts[0], parts[1], " ".join(parts[2:]), role_row[0] if role_row else None, user_id),
        )


def ensure_schema(db_path=None):
    """Приводит БД к схеме, нужной приложению (идемпотентно)."""
    conn = sqlite3.connect(db_path or config.DB_PATH, isolation_level=None)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        if _table_exists(conn, "Заказ"):
            _make_order_header_flexible(conn)
        conn.execute("BEGIN")
        _create_order_items(conn)
        _create_roles_and_users(conn)
        conn.execute("COMMIT")
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    ensure_schema()
    print("✅ Схема БД готова: Состав_заказа, Роль, Пользователь (фамилия, имя, отчество, роль_id)")
