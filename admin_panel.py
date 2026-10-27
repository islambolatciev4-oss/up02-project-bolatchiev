"""Админ-панель: просмотр и изменение остатков товаров."""
import tkinter as tk
from tkinter import messagebox, ttk

import database as db
import order_manager as om
from error_handler import safe_call, validate_positive_int
from styles import (
    COLOR_ACCENT, COLOR_MAIN_BG, COLOR_SECONDARY_BG,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font,
)


class AdminPanel:
    """Панель администратора."""

    def __init__(self, parent, current_user=None, on_change=None):
        self.current_user = current_user
        self.on_change = on_change
        self.window = None
        if not (current_user and current_user[db.U_ROLE] == "Администратор"):
            messagebox.showerror("Доступ запрещён", "Админ-панель доступна только администратору")
            return
        self.window = tk.Toplevel(parent)
        self.window.title("Админ-панель — остатки товаров")
        self.window.geometry("720x500")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.build_ui()
        self.load_products()

    def build_ui(self):
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="ОСТАТКИ ТОВАРОВ", font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(pady=12)

        columns = ("id", "name", "category", "qty")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings", height=12)
        for column, title, width in (("id", "№", 50), ("name", "Название", 280),
                                     ("category", "Категория", 160), ("qty", "Остаток", 100)):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

        row = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        row.pack(fill="x", padx=15, pady=10)
        tk.Label(row, text="Новый остаток:", font=font(FONT_SIZE_NORMAL), bg=COLOR_MAIN_BG).pack(side="left")
        self.quantity_entry = tk.Entry(row, font=font(FONT_SIZE_NORMAL), width=8)
        self.quantity_entry.pack(side="left", padx=8)
        tk.Button(row, text="Сохранить", command=self.save_quantity, bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL), padx=10).pack(side="left")

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for product in db.get_all_products():
            self.tree.insert("", "end", iid=str(product[db.P_ID]),
                             values=(product[db.P_ID], product[db.P_NAME],
                                     product[db.P_CATEGORY], product[db.P_QTY]))

    def save_quantity(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Остатки", "Выберите товар в списке")
            return
        text = self.quantity_entry.get().strip()
        try:
            quantity = 0 if text == "0" else validate_positive_int(text, "Остаток")
        except ValueError as error:
            messagebox.showwarning("Некорректные данные", str(error))
            return
        safe_call(om.update_product_quantity, int(selection[0]), quantity)
        self.load_products()
        if self.on_change:
            self.on_change()
