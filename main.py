"""Главное окно приложения «Доставка еды»: каталог, роли, заказы.

Запуск:  python main.py
Логины для входа: client1, client2 (Клиент), manager1 (Менеджер), admin1 (Администратор).
"""
import tkinter as tk
from tkinter import messagebox

import database as db
from db_migrate import ensure_schema
from error_handler import safe_call
from main_catalog import CatalogWindow
from order_manager import create_order
from styles import COLOR_ACCENT, FONT_SIZE_NORMAL, font


class MainWindow(CatalogWindow):
    """Каталог + авторизация + кнопки по ролям."""

    def __init__(self):
        super().__init__()
        self.current_user = None
        self.on_add_to_order = self.make_order
        self.load_products()          # перерисовать карточки с оформлением заказа
        self.root.after(100, self.require_auth)

    def require_auth(self):
        """Запрашивает авторизацию."""
        from auth import AuthWindow
        AuthWindow(self.root, self.on_auth_success)

    def on_auth_success(self, user):
        """
        Обработчик успешной авторизации.

        :param user: кортеж (id, фамилия, имя, отчество, логин, роль)
        """
        self.current_user = user
        self.user_label.config(text=f"{self.get_user_fio()} ({user[db.U_ROLE]})")
        self.add_role_buttons(user[db.U_ROLE])

    def get_user_fio(self):
        """ФИО текущего пользователя."""
        user = self.current_user
        return f"{user[db.U_LAST]} {user[db.U_FIRST]} {user[db.U_MIDDLE] or ''}".strip()

    def add_role_buttons(self, role):
        """Добавляет кнопки в зависимости от роли."""
        if role in ("Менеджер", "Администратор"):
            tk.Button(self.header, text="Заказы", command=self.open_orders,
                      bg=COLOR_ACCENT, fg="white", font=font(FONT_SIZE_NORMAL),
                      padx=10, pady=5).pack(side="right", padx=10)
        if role == "Администратор":
            tk.Button(self.header, text="Админ-панель", command=self.open_admin,
                      bg=COLOR_ACCENT, fg="white", font=font(FONT_SIZE_NORMAL),
                      padx=10, pady=5).pack(side="right", padx=10)

    def make_order(self, product, quantity):
        """Оформляет заказ текущего пользователя (вызывается из формы просмотра)."""
        if self.current_user is None:
            raise ValueError("Сначала войдите в систему")
        create_order(self.get_user_fio(), [(product[db.P_ID], quantity)])

    def open_orders(self):
        """Открывает список заказов."""
        from orders_window import OrdersWindow
        safe_call(OrdersWindow, self.root, self.current_user)

    def open_admin(self):
        """Открывает админ-панель."""
        from admin_panel import AdminPanel
        safe_call(AdminPanel, self.root, self.current_user, self.refresh_catalog)


def main():
    try:
        ensure_schema()
    except Exception as error:
        messagebox.showerror("База данных", f"Не удалось подготовить БД:\n{error}")
        return
    MainWindow().run()


if __name__ == "__main__":
    main()
