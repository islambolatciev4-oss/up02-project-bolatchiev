"""Проверка проекта: пустые файлы, отсутствующие модули, синтаксические ошибки.

Запуск:  python check_files.py
Помогает вовремя заметить файл, который не сохранился (0 байт) или потерялся.
"""
import os
import py_compile
import sys

REQUIRED = [
    "config.py", "database.py", "db_migrate.py", "styles.py", "styles_colors.py",
    "resources.py", "catalog.py", "catalog_logic.py", "main_catalog.py", "main.py",
    "view_form.py", "error_handler.py", "order_manager.py", "orders_window.py",
    "order_items_window.py", "auth.py", "admin_panel.py", "discount.py", "models.py",
    "db_products.py", "db_orders.py",
    "resources/picture.png", "resources/logo.png", "resources/icon.ico",
    "databases/db_variant_22.db",
]


def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    problems = 0

    print("=" * 60)
    print("ПРОВЕРКА ФАЙЛОВ ПРОЕКТА")
    print("=" * 60)

    for name in REQUIRED:
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            print(f"❌ НЕТ ФАЙЛА: {name}")
            problems += 1
        elif os.path.getsize(path) == 0:
            print(f"❌ ПУСТОЙ (0 байт): {name}  — код не сохранился, вставьте его заново")
            problems += 1

    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if name.endswith(".py") and os.path.getsize(path) == 0 and name not in REQUIRED:
            print(f"⚠️  пустой файл: {name}")
        elif name.endswith(".py") and os.path.getsize(path) > 0:
            try:
                py_compile.compile(path, doraise=True)
            except py_compile.PyCompileError as error:
                print(f"❌ ОШИБКА СИНТАКСИСА в {name}: {error.msg.strip()}")
                problems += 1

    print("=" * 60)
    print("Всё в порядке" if problems == 0 else f"Найдено проблем: {problems}")
    return problems == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
