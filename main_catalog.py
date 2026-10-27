"""Главное окно с каталогом товаров (пары 10–15)."""
import os
import tkinter as tk
from tkinter import ttk

import database as db
from catalog import create_product_card
from config import APP_TITLE
from resources import PATH_ICON, PATH_LOGO, load_image_proportional
from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font,
)


def set_app_icon(root, icon_path):
    """Устанавливает иконку приложения кроссплатформенно."""
    try:
        if os.name == "nt":   # Windows
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        else:                 # Linux / Mac
            png_path = icon_path.replace(".ico", ".png")
            icon_img = load_image_proportional(png_path, max_size=(32, 32))
            if icon_img:
                root.iconphoto(True, icon_img)
                root._icon_photo = icon_img   # сохраняем ссылку
    except Exception as error:
        print(f"Не удалось установить иконку: {error}")


class CatalogWindow:
    """Окно каталога: шапка с логотипом и прокручиваемый список карточек."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("950x700")
        self.root.configure(bg=COLOR_MAIN_BG)
        set_app_icon(self.root, PATH_ICON)
        self.on_add_to_order = None   # в MainWindow заменяется на оформление заказа
        self.build_ui()
        self.load_products()

    def build_ui(self):
        """Строит шапку и область с прокруткой."""
        self.header = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=80)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        logo = load_image_proportional(PATH_LOGO, max_size=(60, 60))   # не искажаем!
        if logo:
            logo_label = tk.Label(self.header, image=logo, bg=COLOR_SECONDARY_BG)
            logo_label.image = logo
            logo_label.pack(side="left", padx=15)
        else:
            tk.Label(self.header, text="[ЛОГОТИП]", bg=COLOR_SECONDARY_BG).pack(side="left", padx=15)

        self.user_label = tk.Label(self.header, text="", font=font(FONT_SIZE_NORMAL),
                                   bg=COLOR_SECONDARY_BG)
        self.user_label.pack(side="right", padx=15)

        tk.Label(self.header, text="КАТАЛОГ ТОВАРОВ", font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(expand=True)

        self.canvas = tk.Canvas(self.root, bg=COLOR_MAIN_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.catalog_frame = tk.Frame(self.canvas, bg=COLOR_MAIN_BG)
        self.catalog_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.window_id = self.canvas.create_window((0, 0), window=self.catalog_frame, anchor="nw")
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfig(self.window_id, width=event.width),
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def load_products(self):
        """Загружает товары из БД и создаёт карточки."""
        for widget in self.catalog_frame.winfo_children():
            widget.destroy()
        try:
            products = db.get_all_products()
        except Exception as error:   # приложение не должно падать
            print(f"[ERROR] Не удалось загрузить товары: {error}")
            tk.Label(self.catalog_frame, text=f"Не удалось загрузить каталог:\n{error}",
                     bg=COLOR_MAIN_BG, font=font(FONT_SIZE_NORMAL)).pack(pady=30)
            return
        if not products:
            tk.Label(self.catalog_frame, text="Каталог пуст", bg=COLOR_MAIN_BG,
                     font=font(FONT_SIZE_NORMAL)).pack(pady=30)
            return
        for product in products:
            create_product_card(self.catalog_frame, product,
                                refresh=self.refresh_catalog,
                                on_add_to_order=self.on_add_to_order)

    def refresh_catalog(self):
        """Перечитывает товары (после заказа остатки изменились)."""
        self.load_products()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CatalogWindow().run()
