"""Авторизация: вход только по логину из списка пользователей (пароль не нужен)."""
import tkinter as tk
from tkinter import messagebox

import database as db
from styles import (
    COLOR_ACCENT, COLOR_MAIN_BG, COLOR_SECONDARY_BG,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font,
)


class AuthWindow:
    """Окно входа."""

    def __init__(self, root, on_success):
        """
        :param root: главное окно
        :param on_success: функция, которой передаётся пользователь после входа
        """
        self.root = root
        self.on_success = on_success

        self.window = tk.Toplevel(root)
        self.window.title("Авторизация")
        self.window.geometry("380x230")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.window.transient(root)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="ВХОД В СИСТЕМУ", font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(pady=12)

        body = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        body.pack(fill="both", expand=True, padx=25, pady=15)
        tk.Label(body, text="Логин:", font=font(FONT_SIZE_NORMAL), bg=COLOR_MAIN_BG,
                 anchor="w").pack(fill="x")
        self.login_entry = tk.Entry(body, font=font(FONT_SIZE_NORMAL))
        self.login_entry.pack(fill="x", pady=5)
        self.login_entry.focus_set()
        self.login_entry.bind("<Return>", lambda event: self.login())
        tk.Button(body, text="Войти", command=self.login, bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL), padx=15, pady=5).pack(pady=10)

    def login(self):
        """Проверяет логин и пускает пользователя в систему."""
        login = self.login_entry.get().strip()
        if not login:
            messagebox.showwarning("Вход", "Введите логин")
            return
        try:
            user = db.get_user_by_login(login)
        except Exception as error:
            messagebox.showerror("Ошибка базы данных", f"Не удалось проверить логин:\n{error}")
            return
        if user is None:
            messagebox.showerror("Вход", "Пользователь с таким логином не найден")
            return
        self.window.grab_release()
        self.window.destroy()
        self.on_success(user)

    def on_close(self):
        """Закрытие окна входа без авторизации завершает приложение."""
        self.root.destroy()
