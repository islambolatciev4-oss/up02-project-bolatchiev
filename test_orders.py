"""Тесты заказов, остатков, JOIN, ролей. Работают с КОПИЕЙ базы — ваша БД не меняется."""
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime

# Подмена пути к БД ДО импорта модулей проекта
_tmp_dir = tempfile.mkdtemp()
_tmp_db = os.path.join(_tmp_dir, "test.db")
_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", "db_variant_22.db")
shutil.copy(_src, _tmp_db)
os.environ["UP02_DB_PATH"] = _tmp_db

import database as db                      # noqa: E402
import db_migrate                          # noqa: E402
import order_manager as om                 # noqa: E402

db_migrate.ensure_schema()


def stock(product_id):
    return om.get_product_quantity(product_id)


def raises(func, *args):
    try:
        func(*args)
    except ValueError:
        return True
    return False


def run_tests():
    today = datetime.now().strftime("%Y-%m-%d")
    checks = []

    def check(name, ok):
        checks.append((name, bool(ok)))

    # --- миграция / старые данные
    check("Старые заказы перенесены в Состав_заказа", len(om.get_order_items(1)) == 1)
    check("Сумма старого заказа №1 = 1200", om.get_order_total(1) == 1200)

    # --- оформление заказа (INSERT + UPDATE)
    before = stock(1)
    order_id = om.create_order("Тест Клиент", [(1, 2), (4, 1)])
    check("Заказ создан, id больше предыдущего", order_id == om.get_last_order_id())
    check("Остаток Маргариты уменьшился на 2", stock(1) == before - 2)
    items = om.get_order_items(order_id)
    check("В составе две позиции (JOIN)", len(items) == 2 and items[0][1] == "Маргарита")
    check("Дата заказа — сегодня", om.get_order_by_id(order_id)[1] == today)
    check("Цена позиции записана числом", isinstance(items[0][3], float))

    # --- ошибки: откат транзакции
    cnt = len(om.get_all_orders())
    before = stock(2)
    check("Не хватает остатка → ValueError", raises(om.create_order, "Тест", [(2, 999)]))
    check("После ошибки заказ не создан", len(om.get_all_orders()) == cnt)
    check("После ошибки остаток не изменился", stock(2) == before)
    check("Несуществующий товар → ValueError", raises(om.create_order, "Тест", [(999, 1)]))
    check("Нулевое количество → ValueError", raises(om.create_order, "Тест", [(1, 0)]))
    check("Пустой заказ → ValueError", raises(om.create_order, "Тест", []))
    check("Откат всей транзакции: первая позиция тоже не списана",
          raises(om.create_order, "Тест", [(1, 1), (2, 999)]) and stock(1) == om.get_product_quantity(1))

    # --- список заказов, поиск
    check("get_all_orders: новые сверху", om.get_all_orders()[0][0] == om.get_last_order_id())
    check("get_orders_by_client", len(om.get_orders_by_client("Иванов Иван Иванович")) == 2)

    # --- администратор: дата и удаление позиции
    om.update_order_date(order_id, "2026-10-01")
    check("Дата заказа изменена", om.get_order_by_id(order_id)[1] == "2026-10-01")
    check("Неверный формат даты → ValueError", raises(om.update_order_date, order_id, "01.10.2026"))
    check("Несуществующий заказ → ValueError", raises(om.update_order_date, 99999, "2026-10-01"))
    before = stock(1)
    om.delete_order_item(items[0][0])
    check("Позиция удалена из состава", len(om.get_order_items(order_id)) == 1)
    check("Товар вернулся на склад", stock(1) == before + 2)
    check("Удаление несуществующей позиции → ValueError", raises(om.delete_order_item, 99999))

    # --- остатки
    om.update_product_quantity(7, 3)
    check("Остаток установлен вручную", stock(7) == 3)
    check("Отрицательный остаток → ValueError", raises(om.update_product_quantity, 7, -1))

    # --- пользователи и роли
    users = {u[4]: u[5] for u in db.get_all_users()}
    check("4 пользователя", len(users) == 4)
    check("Роли: клиент / менеджер / администратор",
          users.get("client1") == "Клиент" and users.get("manager1") == "Менеджер"
          and users.get("admin1") == "Администратор")
    check("Неизвестный логин → None", db.get_user_by_login("нет_такого") is None)
    check("ФИО разбито на фамилию, имя, отчество", db.get_user_by_login("admin1")[1:4] == ("Кузнецова", "Мария", "Дмитриевна"))

    # --- скидка в заказе: Цезарь (нет заказов в прошлом месяце) → 25%
    order2 = om.create_order("Скидка", [(4, 1)], date="2026-10-15")
    price = om.get_order_items(order2)[0][3]
    check("Скидка 25% попала в заказ (Цезарь 350 → 262.5)", price == 262.5)
    order3 = om.create_order("Скидка", [(1, 1)], date="2026-10-15")
    check("Заказ в сентябре влияет на скидку в октябре: Маргарита 15.10 → 600",
          om.get_order_items(order3)[0][3] == 600)

    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАКАЗОВ, ОСТАТКОВ, РОЛЕЙ")
    print("=" * 70)
    passed = 0
    for name, ok in checks:
        passed += ok
        print(f"{'✅' if ok else '❌'} {name}")
    print("=" * 70)
    print(f"Пройдено: {passed} / {len(checks)}")
    shutil.rmtree(_tmp_dir, ignore_errors=True)
    return passed == len(checks)


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
