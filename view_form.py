"""Форма просмотра выбранного товара."""
import tkinter as tk
from tkinter import messagebox

import database as db
from catalog import _indicator, get_price_text
from error_handler import validate_positive_int
from resources import get_product_image
from styles import (
    COLOR_ACCENT, COLOR_MAIN_BG, COLOR_SECONDARY_BG,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font,
)


class ViewForm:
    """Форма просмотра товара. Открывается кликом по карточке в каталоге."""

    def __init__(self, parent, product, on_add_to_order=None, refresh=None):
        """
        :param parent: родительское окно
        :param product: кортеж товара из БД
        :param on_add_to_order: функция оформления заказа (product, quantity)
        :param refresh: функция обновления каталога
        """
        self.product = product
        self.on_add_to_order = on_add_to_order
        self.refresh = refresh

        name = product[db.P_NAME] if product and product[db.P_NAME] else "[Без названия]"
        self.window = tk.Toplevel(parent)
        self.window.title(f"Просмотр — {name}")
        self.window.geometry("720x520")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.build_ui()

    def build_ui(self):
        """Строит интерфейс формы."""
        product = self.product

        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="КАРТОЧКА ТОВАРА", font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(pady=15)

        main = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        img_frame = tk.Frame(main, bg=COLOR_MAIN_BG)
        img_frame.pack(side="left", padx=10, anchor="n")
        photo = get_product_image(product[db.P_IMAGE], size=(200, 200))
        if photo:
            img_label = tk.Label(img_frame, image=photo, bg=COLOR_MAIN_BG)
            img_label.image = photo
            img_label.pack()

        info_frame = tk.Frame(main, bg=COLOR_MAIN_BG)
        info_frame.pack(side="left", fill="both", expand=True, padx=20)

        qty = product[db.P_QTY] if product[db.P_QTY] is not None else 0
        self._add_field(info_frame, "Наименование", product[db.P_NAME] or "[Без названия]")
        self._add_field(info_frame, "Категория", product[db.P_CATEGORY] or "[Без категории]")
        self._add_field(info_frame, "Вес", f"{product[db.P_WEIGHT] or 0} г")
        self._add_field(info_frame, "Цена со скидкой", get_price_text(product))
        self._add_field(info_frame, "Состав", product[db.P_COMPOSITION] or "[Не указан]")
        self._add_field(info_frame, "В наличии", f"{_indicator(qty)} ({qty})")

        # Количество для заказа
        row = tk.Frame(info_frame, bg=COLOR_MAIN_BG)
        row.pack(fill="x", pady=8)
        tk.Label(row, text="Количество:", font=font(FONT_SIZE_NORMAL, bold=True),
                 bg=COLOR_MAIN_BG, width=15, anchor="w").pack(side="left")
        self.quantity_var = tk.StringVar(value="1")
        tk.Spinbox(row, from_=1, to=max(qty, 1), width=6, textvariable=self.quantity_var,
                   font=font(FONT_SIZE_NORMAL)).pack(side="left")

        btn_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="Добавить в заказ", command=self.add_to_order,
                  bg=COLOR_ACCENT, fg="white", font=font(FONT_SIZE_NORMAL),
                  padx=15, pady=5).pack(side="left", padx=20)
        tk.Button(btn_frame, text="Назад", command=self.window.destroy,
                  bg=COLOR_ACCENT, fg="white", font=font(FONT_SIZE_NORMAL),
                  padx=15, pady=5).pack(side="right", padx=20)

    def _add_field(self, parent, label, value):
        """
        Добавляет строку «название: значение».

        :param parent: родительский фрейм
        :param label: название поля
        :param value: значение
        """
        row = tk.Frame(parent, bg=COLOR_MAIN_BG)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=f"{label}:", font=font(FONT_SIZE_NORMAL, bold=True),
                 bg=COLOR_MAIN_BG, width=15, anchor="w").pack(side="left")
        tk.Label(row, text=str(value), font=font(FONT_SIZE_NORMAL), bg=COLOR_MAIN_BG,
                 anchor="w", justify="left", wraplength=320).pack(side="left")

    def add_to_order(self):
        """Обработчик кнопки «Добавить в заказ»."""
        if not self.on_add_to_order:
            messagebox.showinfo("Информация", "Функция в разработке")
            return
        if not self.product:
            messagebox.showerror("Ошибка", "Товар не выбран")
            return

        stock = self.product[db.P_QTY] or 0
        if stock <= 0:
            messagebox.showwarning("Нет в наличии", "Этого товара сейчас нет в наличии")
            return
        try:
            quantity = validate_positive_int(self.quantity_var.get(), "Количество", max_value=stock)
            self.on_add_to_order(self.product, quantity)
        except ValueError as error:
            messagebox.showwarning("Некорректные данные", str(error))
            return
        except Exception as error:
            messagebox.showerror("Ошибка заказа", f"Не удалось добавить товар:\n{error}")
            return

        messagebox.showinfo("Успех", f"Заказ оформлен: {self.product[db.P_NAME]} × {quantity}")
        if self.refresh:
            self.refresh()
        self.window.destroy()
