"""Показывает структуру БД: таблицы, поля, типы, количество записей и первые строки."""
import sqlite3

from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
tables = [
    r[0]
    for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    )
]

for table in tables:
    count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    print("=" * 60)
    print(f"Таблица «{table}» — записей: {count}")
    print("=" * 60)
    print(f"{'№':<3} {'Поле':<14} {'Тип':<10} Первичный ключ")
    for cid, name, ctype, notnull, default, pk in conn.execute(f'PRAGMA table_info("{table}")'):
        print(f"{cid + 1:<3} {name:<14} {ctype:<10} {'да' if pk else ''}")
    print("\nПервые строки:")
    for row in conn.execute(f'SELECT * FROM "{table}" LIMIT 3'):
        print("  ", row)
    print()

conn.close()
