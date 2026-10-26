"""Выполняет SQL-запросы к БД прямо из VS Code и печатает результат таблицей.

Запуск:
    python run_sql.py                      - выполнит queries.sql
    python run_sql.py queries_pair3.sql    - выполнит указанный файл
    python run_sql.py -i                   - режим консоли: вводите запросы вручную
"""
import sqlite3
import sys

from config import DB_PATH


def print_table(columns, rows):
    """Печатает результат запроса в виде таблицы."""
    if not rows:
        print("   (пусто — подходящих записей нет)")
        return
    data = [[("" if v is None else str(v)) for v in row] for row in rows]
    widths = [
        max(len(str(col)), *(len(r[i]) for r in data))
        for i, col in enumerate(columns)
    ]
    line = "   " + " | ".join(str(c).ljust(w) for c, w in zip(columns, widths))
    print(line)
    print("   " + "-+-".join("-" * w for w in widths))
    for r in data:
        print("   " + " | ".join(v.ljust(w) for v, w in zip(r, widths)))
    print(f"   Строк: {len(rows)}")


def run_statement(conn, sql):
    """Выполняет один запрос и выводит результат."""
    try:
        cur = conn.execute(sql)
        if cur.description:                      # SELECT
            columns = [d[0] for d in cur.description]
            print_table(columns, cur.fetchall())
        else:                                    # INSERT / UPDATE / DELETE
            conn.commit()
            print(f"   Готово. Изменено строк: {cur.rowcount}")
    except sqlite3.Error as e:
        print(f"   ❌ Ошибка SQL: {e}")


def run_file(path):
    """Читает .sql-файл и выполняет запросы по очереди."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    conn = sqlite3.connect(DB_PATH)
    buffer = ""
    comment = ""
    number = 0
    for line in lines:
        stripped = line.strip()
        if not buffer and stripped.startswith("--"):
            text = stripped.lstrip("-").strip()
            if text and not set(text) <= {"=", "-"}:
                comment = text
            continue
        if not buffer and not stripped:
            continue
        buffer += line + "\n"
        if sqlite3.complete_statement(buffer):
            number += 1
            print(f"\n[{number}] {comment}" if comment else f"\n[{number}]")
            print("   " + " ".join(buffer.split()))
            run_statement(conn, buffer)
            buffer = ""
            comment = ""
    conn.close()
    print(f"\nВыполнено запросов: {number}")


def interactive():
    """Консоль: вводите SQL, запрос заканчивается точкой с запятой."""
    conn = sqlite3.connect(DB_PATH)
    print("SQL-консоль. Запрос заканчивайте символом ';'. Выход: пустая строка или exit.")
    buffer = ""
    while True:
        try:
            line = input("sql> " if not buffer else "...> ")
        except EOFError:
            break
        if not buffer and line.strip().lower() in ("", "exit", "quit"):
            break
        buffer += line + "\n"
        if sqlite3.complete_statement(buffer):
            run_statement(conn, buffer)
            buffer = ""
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        interactive()
    else:
        run_file(sys.argv[1] if len(sys.argv) > 1 else "queries.sql")
