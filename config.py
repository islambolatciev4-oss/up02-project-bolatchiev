"""Настройки проекта (SQLite)."""
import os

# Путь к БД считается от папки проекта, поэтому работает из любого места запуска
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "databases", "db_variant_22.db")
